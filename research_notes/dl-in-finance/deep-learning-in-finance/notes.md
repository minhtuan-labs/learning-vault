# 📄 Paper Notes — Deep Learning in Finance
**Authors:** J. B. Heaton, N. G. Polson and J.H. Witte (February 2016)  
**Link:** [arXiv:1602.06561v3](https://arxiv.org/abs/1602.06561v3)  
**Tags:** #deep-learning #machine-learning #big-data #ai #lstm-model #finance #asset-pricing #volatility
**PDF:** [deep-learning-in-finance](deep-learning-in-finance.pdf)

---

## 🧩 Abstract (tóm tắt)
The paper introduces the use of deep learning hierarchical models for problems in financial prediction and classification.

---

## 🧠 Key Ideas
- Replace recurrent layers with multi-head self-attention.
- Position encoding added to preserve sequence order.
- Parallel computation enables better scalability.

---

## 🔬 Technical Highlights
| Concept | Explanation |
|----------|--------------|
| Attention mechanism | Computes relevance between tokens using Q, K, V matrices. |
| Multi-head | Enables multiple representation subspaces. |
| Position encoding | Adds sequential information to embeddings. |

---

## 📈 Strengths / Limitations
**Strengths**
- High parallelism
- SOTA performance in translation

**Limitations**
- Requires large datasets
- Memory cost ∝ sequence length²

---

## 💡 My Takeaways
- Self-attention unlocks architecture generalization power.
- Inspired me to explore applying attention to tabular data.

---

## 📚 References
- [Annotated Transformer by Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
- [The Illustrated Transformer (Jay Alammar)](https://jalammar.github.io/illustrated-transformer/)