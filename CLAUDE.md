# Project: aadhilanwar.dev

Personal portfolio site for Aadhil Anwar, security engineer at GoDaddy.

## Stack

- **Framework:** Jekyll (static site generator)
- **Hosting:** GitHub Pages (repo: `aadhil-anwer/port-new`, branch: `main`)
- **CDN/Cache:** Cloudflare with 14-day cache, auto-purge on deploy via GitHub Actions
- **Custom domain:** aadhilanwar.dev
- **Fonts:** Inter (body), JetBrains Mono (code/headings) via Google Fonts
- **Theme:** Custom dark theme ("Quiet Authority" design system), no Jekyll theme gem

## Structure

```
_config.yml          - Jekyll config, url: https://aadhilanwar.dev
CNAME                - Custom domain file for GitHub Pages
Gemfile              - github-pages, jekyll-seo-tag, jekyll-sitemap

_layouts/
  default.html       - Main wrapper (nav, main, footer, loads main.js)
  post.html          - Blog post layout with Schema.org BlogPosting

_includes/
  head.html          - Meta tags, fonts, CSS link
  nav.html           - Navigation bar with mobile hamburger
  footer.html        - Site footer
  icons/             - SVG icon partials

_data/
  social.yml         - Social links (GitHub, LinkedIn, X)
  projects.yml       - Projects list with tech tags
  certifications.yml - Certs
  achievements.yml   - Achievements
  talks.yml          - Speaking engagements
  books.yml          - Bookshelf entries

_posts/              - Blog posts (markdown)
_writeups/           - Security writeups collection

css/style.css        - All styles (~1345 lines), CSS variables, responsive
js/main.js           - Mobile nav toggle (~24 lines)
images/              - headshot.jpg, og-default.png, blog images

Pages:
  index.html         - Homepage with hero, bio, social links, recent posts
  about.html         - About page with resume data, JSON-LD
  blog.html          - Blog listing
  bookshelf.html     - Reading list
  projects.html      - Projects showcase
  contact.html       - Contact info
  writeups.html      - Security writeups
  404.html           - Error page
```

## Build & Deploy

- GitHub Actions workflow: `.github/workflows/jekyll.yml`
- On push to `main`: checkout > setup Ruby 3.1 > bundle install > jekyll build > deploy to GitHub Pages > purge Cloudflare cache
- Cloudflare cache purge uses `CLOUDFLARE_ZONE_ID` and `CLOUDFLARE_API_TOKEN` repo secrets

## SEO

- jekyll-seo-tag plugin for meta tags
- JSON-LD Person schema on homepage (skills, credentials, employer)
- BlogPosting schema on posts
- Open Graph and Twitter card meta
- robots.txt allows AI crawlers (GPTBot, Claude, etc.)
- sitemap.xml auto-generated
- RSS feed via jekyll-feed
- llms.txt and llms-full.txt for LLM context

## Design

- Dark-only theme with 4-tier elevation backgrounds
- 13+ CSS custom properties for colors
- Responsive breakpoints at 768px and 900px
- Hamburger nav on mobile with outside-click close
- Hero section with headshot and fallback initials
- Smooth transitions, respects prefers-reduced-motion
