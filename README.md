# aadhilanwar.github.io

Personal portfolio and blog. Built with Jekyll, deployed on GitHub Pages.

## Local Development

```bash
gem install bundler
bundle install
bundle exec jekyll serve
```

Then open `http://localhost:4000`.

## Adding a Blog Post

Create a new file in `_posts/` with the format `YYYY-MM-DD-slug.md`:

```markdown
---
title: "Your Post Title"
description: "A short description."
date: 2026-04-05
tags: [security, networking]
type: blog
---

Your content here in Markdown.
```

## Adding a Writeup

Same format, but in `_writeups/`:

```markdown
---
title: "CTF Name — Challenge Name"
description: "Short description."
date: 2026-04-05
tags: [ctf, web]
type: writeup
---

Your writeup content here.
```

## Deploy to GitHub Pages

1. Push to a repo named `aadhilanwar.github.io`
2. Go to Settings > Pages > Source: Deploy from branch (main)
3. Site will be live at `https://aadhilanwar.github.io`
