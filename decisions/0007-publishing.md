# 0007 How an approved edition is published

- Question: how does an edition get from the merge into `main` onto the website, and what does Buttondown host?
- Options: a GitHub Action that renders and deploys to Netlify; rendering locally into `docs/`; `quarto publish netlify` by hand. For Buttondown: the free archive, or the archive on a paid subdomain (about USD 29 per month).
- Choice: the merge into `main` starts a GitHub Action that renders with R and Quarto and deploys to Netlify. Buttondown keeps its free archive, and each email points to its copy on the website through a canonical URL.
- Why: my yes stays the only manual step, and rendered HTML stays out of Git. Netlify already hosts my other two websites and works from a private repository. A paid subdomain would show the same editions twice.
- Date: 2026-10-15
