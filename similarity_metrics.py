import numpy as np
from scipy.special import rel_entr

# l1 Norm and Jaccard's Coefficient
def l1_norm(q, r):
    """
    Calculates the L1 norm (Manhattan distance) between two vectors.
    Formula: sum(|q(v) - r(v)|)
    """
    q = np.array(q)
    r = np.array(r)
    # Using the built-in numpy linalg function
    return np.linalg.norm(q - r, ord=1)

def jaccard_coefficient(q, r):
    """
    Calculates Jaccard's coefficient based on the provided formula.
    It measures the ratio of the intersection of non-zero elements 
    to the union of non-zero elements.
    """
    q = np.array(q)
    r = np.array(r)
    
    # Intersection: indices where both q and r are > 0
    intersection = np.logical_and(q > 0, r > 0).sum()
    
    # Union: indices where either q or r (or both) are > 0
    union = np.logical_or(q > 0, r > 0).sum()
    
    if union == 0:
        return 0.0
    return intersection / union

# --- Example Usage ---
q_vec = [0.1, 0.5, 0.0, 0.8]
r_vec = [0.2, 0.0, 0.3, 0.7]

print(f"L1 Norm: {l1_norm(q_vec, r_vec):.4f}")
print(f"Jaccard Coefficient: {jaccard_coefficient(q_vec, r_vec):.4f}")
# --------------------------------------

# Confusion Probability (original)
def confusion_probability(q, P_m_cond):
    """
    Calculates the confusion probability conf(q, r, P(m)).
    
    Parameters:
    q (array-like): Probability vector q
    P_m_cond (array-like): Conditional probabilities P(m|v) for each v (does not sum to 1)
    """
    # Convert inputs to numpy arrays for vectorization
    q = np.array(q)
    P_m_cond = np.array(P_m_cond)

    # Calculate the formula: sum over v of [q(v) * P(m|v)]
    result = np.sum(q * P_m_cond)
    
    return result

# --- Example Usage ---
q_vec = [0.2, 0.4, 0.1]
# Representing P(m|v)
P_m_cond_vec = [0.15, 0.5, 0.05] 

conf_val = confusion_probability(q_vec, P_m_cond_vec)
print(f"Confusion Probability: {conf_val:.4f}")
# --------------------------------------

# Confusion Probability (min)
def min_confusion_probability(q, P_m_cond):
    """
    Calculates the confusion probability conf(q, r, P(m)) using the 
    minimum of the two components instead of their product.
    
    Parameters:
    q (array-like): Probability vector q
    P_m_cond (array-like): Conditional probabilities P(m|v) for each v 
    """
    # Convert inputs to numpy arrays for vectorization
    q = np.array(q)
    P_m_cond = np.array(P_m_cond)

    # Calculate the formula: sum over v of [ min(q(v), P_m_cond(v)) ]
    # We use np.minimum for element-wise comparison
    result = np.sum(np.minimum(q, P_m_cond))
    
    return result

# --- Example Usage ---
q_vec = [0.2, 0.4, 0.1]
# Representing P(m|v)
P_m_cond_vec = [0.15, 0.5, 0.05] 

conf_val = min_confusion_probability(q_vec, P_m_cond_vec)
print(f"Min Confusion Probability: {conf_val:.4f}")
# --------------------------------------

# Other similarity metrics (Cosine Similarity, Jensen-Shannon Divergence)

def cosine_similarity(q, r):
    """
    Calculates cosine similarity between two vectors.
    """
    q = np.array(q)
    r = np.array(r)
    
    numerator = np.sum(q * r)
    denominator = np.sqrt(np.sum(q**2)) * np.sqrt(np.sum(r**2))
    
    if denominator == 0:
        return 0.0
    return numerator / denominator

def kl_divergence(p, q):
    """
    Calculates the KL divergence D(p || q).
    Uses scipy.special.rel_entr for numerical stability.
    """
    # rel_entr(p, q) computes p * log(p/q)
    return np.sum(rel_entr(p, q))

def jensen_shannon_divergence(q, r):
    """
    Calculates the Jensen-Shannon divergence JS(q, r).
    """
    q = np.array(q)
    r = np.array(r)
    
    # Calculate the average distribution: (q + r) / 2
    avg = 0.5 * (q + r)
    
    # JS(q, r) = 0.5 * D(q || avg) + 0.5 * D(r || avg)
    js = 0.5 * kl_divergence(q, avg) + 0.5 * kl_divergence(r, avg)
    
    return js

# --- Example Usage ---
q_vec = [0.1, 0.5, 0.4]
r_vec = [0.2, 0.3, 0.5]

print(f"Cosine Similarity: {cosine_similarity(q_vec, r_vec):.4f}")
print(f"JS Divergence: {jensen_shannon_divergence(q_vec, r_vec):.4f}")


