# Context Engineering - Advanced RAG Optimization

**Optimizar RAG para producción: semantic caching, compression, vector DB tuning**

---

## 🎯 Objetivo

Reducir costos y latencia de RAG en producción.

**Resultados:**
- 70% reducción en costos de embeddings (caching)
- 50% reducción en latency (compression + optimization)
- 90% hit rate en semantic cache

---

## 📋 Cuándo Optimizar

**Señales de que necesitas esto:**
- [ ] Costos de OpenAI embeddings >$500/mes
- [ ] p95 latency de RAG >3 segundos
- [ ] Queries repetitivas (misma pregunta, diferentes palabras)
- [ ] Vector DB costs creciendo sin control

**NO optimices si:**
- ❌ <100 usuarios
- ❌ Costos <$100/mes
- ❌ Latency acceptable (<1s)

---

## 🚀 PASO 1: Semantic Caching

### 1.1 Concept

**Problema:** Query similar = re-embed + re-search = $$$

**Solución:** Cache semánticamente similar queries

```python
from sentence_transformers import SentenceTransformer, util
import redis

class SemanticCache:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, small
        self.redis = redis.Redis(host='localhost', port=6379)
        self.similarity_threshold = 0.85  # Tune based on needs

    def get(self, query: str):
        """Check if semantically similar query exists in cache"""
        query_embedding = self.model.encode(query)

        # Get all cached queries
        cached_queries = self.redis.keys("query:*")

        for cached_key in cached_queries:
            cached_embedding = self.redis.get(cached_key + ":embedding")
            similarity = util.cos_sim(query_embedding, cached_embedding)

            if similarity > self.similarity_threshold:
                # Cache hit!
                return self.redis.get(cached_key + ":result")

        return None

    def set(self, query: str, result: any, ttl: int = 3600):
        """Cache query + result"""
        query_embedding = self.model.encode(query)
        key = f"query:{hash(query)}"

        self.redis.setex(key + ":embedding", ttl, query_embedding.tobytes())
        self.redis.setex(key + ":result", ttl, json.dumps(result))

# Usage
cache = SemanticCache()

def rag_query(query: str):
    # Check cache
    cached_result = cache.get(query)
    if cached_result:
        return json.loads(cached_result)  # 🚀 Instant, $0 cost

    # Cache miss → do expensive RAG
    result = expensive_rag_pipeline(query)

    # Cache result
    cache.set(query, result)

    return result
```

**Savings:** 70% cost reduction (70% cache hit rate típico)

---

## 🗜️ PASO 2: Context Compression

### 2.1 Rerank Results

**Problema:** Retrieve top 20, pero solo top 3 son relevantes

**Solución:** Rerank con modelo pequeño antes de LLM

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank_results(query: str, results: list, top_k: int = 3):
    """Rerank vector search results"""
    pairs = [(query, result['text']) for result in results]
    scores = reranker.predict(pairs)

    # Sort by score
    scored_results = list(zip(results, scores))
    scored_results.sort(key=lambda x: x[1], reverse=True)

    return [r for r, s in scored_results[:top_k]]

# Usage
raw_results = vector_search(query, top_k=20)  # Retrieve many
best_results = rerank_results(query, raw_results, top_k=3)  # Keep best

context = "\n\n".join([r['text'] for r in best_results])
```

**Savings:** 80% reduction in context tokens (20 → 3 results)

### 2.2 Smart Chunking

**Malo:** Fixed 500-token chunks (pierde contexto)

**Bueno:** Semantic chunking (split en párrafos/secciones)

```python
def semantic_chunk(text: str, max_chunk_size: int = 500):
    """Chunk text by semantic boundaries (paragraphs, sentences)"""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
```

---

## 🎯 PASO 3: Vector DB Optimization

### 3.1 Pinecone Namespaces

```python
# BAD: Single index for all tenants
index.query(vector, top_k=10, filter={"tenant_id": "t1"})  # Slow filtering

# GOOD: Namespace per tenant
index.query(vector, top_k=10, namespace=f"tenant_{tenant_id}")  # Fast
```

### 3.2 Metadata Filtering

```python
# Upsert with rich metadata
index.upsert([
    ("doc_1", embedding, {
        "tenant_id": "t1",
        "doc_type": "invoice",
        "date": "2025-01",
        "status": "paid"
    })
])

# Query with filters (cheaper than retrieving all)
results = index.query(
    vector,
    top_k=10,
    filter={
        "tenant_id": {"$eq": "t1"},
        "doc_type": {"$eq": "invoice"},
        "date": {"$gte": "2025-01"}
    }
)
```

---

## 📊 Production RAG Architecture

```
┌─────────────┐
│  User Query │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Semantic Cache?  │────YES───► Return cached result (70% hit rate)
└──────┬───────────┘
       │NO
       ▼
┌──────────────────┐
│ Generate Embedding│  ($0.0001/query)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Vector Search    │  (Pinecone with namespace + filters)
│ Top 20 results   │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Rerank Results   │  (CrossEncoder, fast)
│ Keep top 3       │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ LLM Generation   │  (gpt-4o-mini, 3 chunks context)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Cache Result     │  (For future similar queries)
└──────────────────┘
```

---

## 💰 Cost Comparison

| Approach | Cost/1K queries | Latency p95 |
|----------|----------------|-------------|
| **Naive RAG** | $5.00 | 3.5s |
| + Semantic Cache | $1.50 (-70%) | 0.5s |
| + Reranking | $0.80 (-84%) | 1.2s |
| + Optimized Vector DB | $0.50 (-90%) | 0.8s |

---

## 🎓 Key Takeaways

1. **Semantic caching = Biggest win** - 70% cost reduction
2. **Rerank before LLM** - Solo envía contexto relevante
3. **Smart chunking** - Semantic boundaries > fixed size
4. **Namespace isolation** - Pinecone performance boost
5. **Measure first** - Profile antes de optimizar

**ROI:** Si gastas >$500/mes en embeddings, esto se paga en 1 mes.
