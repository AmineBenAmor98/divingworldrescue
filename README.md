# Dive-World & Rescue

This German site builds as static HTML. All content, styles, scripts and media needed for browsing are included.

## Development

From this directory run:

    python3 build.py
    python3 check.py
    python3 -m http.server 8000 --directory dist

Open http://localhost:8000 in a browser. For an offline preview, open dist/index.html directly. The dist directory is the deployable site. Rebuild after editing the source.

## Editing

- content/pages.json contains the interior page content, course fees, rental rates and catalogue photographs.
- src/home.html contains the homepage. src/courses.html and src/info.html hold the course overview, team and contact sections. src/header.html and src/footer.html are shared across pages.
- src/main.css defines the shared layouts and mobile styles.
- src/inquiry.html and src/inquiry.js handle course enquiries. A visitor opens a message in WhatsApp or their email app and sends it there.
- public/assets contains the site media. Product and gallery photographs are stored locally.
- build.py provides the shared page layouts, price and rental views. shop.py renders the shop overview, grouped listings and product pages. Each product marker in content/pages.json supplies the group, name, summary, specifications and price. Its following blocks supply photographs and full catalogue text.

## Release notes

The public menu and content were collected on 24 November 2026. The events page places the imported schedule in an archive. Before a public launch the owner should confirm active prices, availability, course prerequisites and legal text. A missing Monte Mare gallery photo returned HTTP 404 from the source and was omitted. The guestbook shows its published entries. Shop enquiries use the contact channels; the site does not process orders or payments.
