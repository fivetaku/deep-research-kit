# Source Quality Rubric

## Rating System (A-E)

### A - Highest Quality (Primary Sources)
| Criteria | Examples |
|----------|----------|
| Peer-reviewed systematic reviews | Cochrane Reviews, PRISMA-compliant studies |
| Meta-analyses | Statistical aggregations of multiple studies |
| Randomized controlled trials | Clinical trials, A/B testing at scale |
| Official government publications | FDA, NIH, WHO, regulatory bodies |
| Major institution research | MIT, Stanford, Google Research, OpenAI |

**Trust Level**: Can be cited as definitive evidence  
**Verification**: Check DOI, publication venue, author credentials

---

### B - High Quality (Authoritative Sources)
| Criteria | Examples |
|----------|----------|
| Peer-reviewed original research | Journal articles with methodology |
| Official standards documents | ISO, IEEE, W3C specifications |
| Established organization white papers | Gartner, McKinsey, Big Tech research |
| Clinical/practice guidelines | Medical associations, professional bodies |
| Official documentation | Product docs, API references |

**Trust Level**: Strong evidence, verify with A-level if critical  
**Verification**: Check author affiliation, funding disclosure

---

### C - Moderate Quality (Expert Sources)
| Criteria | Examples |
|----------|----------|
| Expert opinion pieces | Named experts with credentials |
| Conference presentations | Academic/industry conferences |
| Case studies | Documented implementations |
| Reputable news analysis | NYT, WSJ, BBC technology sections |
| Industry analyst reports | Paid reports with methodology |

**Trust Level**: Useful for context, verify key claims  
**Verification**: Check author expertise, potential bias

---

### D - Lower Quality (Supporting Sources)
| Criteria | Examples |
|----------|----------|
| Preprints | arXiv, bioRxiv (not peer-reviewed) |
| Expert blog posts | Personal blogs from domain experts |
| Conference abstracts | Preliminary findings |
| Press releases | Company announcements |
| Trade publications | Industry news sites |

**Trust Level**: Use as leads, verify before citing  
**Verification**: Cross-reference with higher-quality sources

---

### E - Use with Caution (Weak Sources)
| Criteria | Examples |
|----------|----------|
| Anonymous sources | Unverifiable claims |
| Opinion without evidence | Hot takes, speculation |
| Outdated information | >3 years for fast-moving fields |
| Clear bias/conflicts | Vendor marketing, advocacy sites |
| Social media posts | Twitter/X threads, Reddit comments |
| AI-generated content | Unverified LLM outputs |

**Trust Level**: Do not cite as evidence  
**Verification**: Only use if no alternatives exist, flag uncertainty

---

## Quality Assessment Checklist

For each source, evaluate:

### Authorship
- [ ] Author clearly identified
- [ ] Author has relevant credentials
- [ ] Author affiliation disclosed
- [ ] No undisclosed conflicts of interest

### Publication
- [ ] Publication date clearly stated
- [ ] Publication venue reputable
- [ ] Peer review or editorial process
- [ ] Still current/relevant

### Content
- [ ] Methodology described (if research)
- [ ] Data sources cited
- [ ] Claims supported by evidence
- [ ] Limitations acknowledged

### Accessibility
- [ ] URL accessible and stable
- [ ] DOI available (for academic)
- [ ] Archive link created (for ephemeral content)

---

## Domain-Specific Adjustments

### Technology/AI
- Preprints may be acceptable (field moves fast)
- Company research blogs (Google AI, OpenAI) often quality
- GitHub repositories count as primary sources for code
- Benchmark papers essential for performance claims

### Medical/Health
- Peer-review mandatory for health claims
- Clinical trial registration required
- FDA/regulatory status must be verified
- Patient population and sample size matter

### Business/Market
- Market size claims need methodology
- Analyst reports vary in quality
- Company financials from SEC filings (A-level)
- Press coverage alone insufficient

### Legal/Policy
- Primary legislation and regulations (A-level)
- Court documents and rulings (A-level)
- Legal analysis from law firms (B-level)
- News coverage of legal matters (C-level)

---

## Minimum Quality Thresholds

| Content Type | Minimum Rating |
|--------------|----------------|
| Definitive claims | A or B |
| Statistics/data | A, B, or C with verification |
| Expert opinions | C or higher |
| Background context | D acceptable |
| Future predictions | C with attribution |

---

## Red Flags - Automatic Quality Reduction

- No author attribution → E
- No date → Reduce by 2 levels
- Broken citations → Reduce by 1 level
- Known retraction → E
- Predatory journal → E
- SEO-optimized content farm → E
- Circular citations (sources cite each other) → Investigate
