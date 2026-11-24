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
- build.py provides the shared page layouts, price and rental views. shop.py renders the shop overview, grouped listings and product pages. editorial.py supplies course, archive, gallery and reference layouts. Each product marker in content/pages.json supplies the group, name, summary, specifications and price. Its following blocks supply photographs and full catalogue text.

## Release notes

The public menu and content were collected on 24 November 2026. The events page places the imported schedule in an archive. Before a public launch the owner should confirm active prices, availability, course prerequisites and legal text. A missing Monte Mare gallery photo returned HTTP 404 from the source and was omitted. The guestbook shows its published entries. Shop enquiries use the contact channels; the site does not process orders or payments.

## Publishing metadata

Set SITE_URL to the final website base URL when building, including a path if the site is served under one. The build then emits absolute canonical, Open Graph page and image URLs. For example, if the final host is https://example.org/:

    SITE_URL=https://example.org/ python3 build.py

Without SITE_URL the build supplies descriptions, titles and a PNG favicon. The production domain must be decided before generating deployment metadata. The DuckDNS preview is separate from this local build. Host-level redirects, DNS and TLS are configured on the chosen host.

## Google reviews

content/google-reviews.json is a manually checked snapshot of the Google Maps listing, verified on 24 November 2026. It supplies the rating, count, named excerpts and source link for the homepage. Update these together after checking the listing. The public page displays the snapshot date. The build loads no Google review widget or tracking script.

The Google G icon is the unmodified Google asset from https://www.gstatic.com/images/branding/product/2x/googleg_48dp.png, stored locally as public/assets/google-g.png.


## Full-site review — 24 November 2026

The site now has four main areas — Tauchen, Erste Hilfe, Ausrüstung and Tauchschule. The homepage exposes six visitor goals immediately, then gives diving, Scubility, first aid, shopping, rental and trips their own sections. Product categories and secondary services have visible explanations and internal destinations. The final step is a contextual enquiry through WhatsApp or email.

The equipment directory searches all catalogue records locally. Repeated product names have one search result with combined searchable terms. Each category also has a filter and a price/name sort. Course fees show required extras before the expandable details. First-aid learning-material prices are explicitly distinguished from practical training costs. Gallery archives lead visitors back to the corresponding courses or upcoming-date enquiry. Header, footer, type scale and contact channels are shared.

The imported content covers 27 source sections. The rebuilt site has 26 imported content pages, a team/contact hub, other navigation/enquiry pages and 100 product listing records, for 131 HTML pages in total. This preserves the offer areas and edited useful information; it is not a verbatim copy of every old sentence, banner or duplicate listing. Original source files remain in work/source-pages at the workspace root.

All local links, images, anchors and enquiry destinations passed check.py. Browser layout sweeps covered all 131 pages at 360, 768 and 1440 pixels, plus the equivalent homepage alias. Shared layouts and representative product pages were visually reviewed. Search, empty results, reset, sorting, the mobile menu, contextual enquiry drafts, animation controls and footer disclosures were exercised without sending messages.

The complete inventory, validation scope and remaining owner confirmations are in content/site-review.json. Before launch, confirm active prices/stock, course prerequisites, future dates, contact hours and legal text. The legal source includes features and references that need review for the new site. Conflicting product prices are shown as enquiries. This remains a catalogue and enquiry website; it has no live stock, cart or payment checkout.

The latest deployable files are in dist. Shared CSS and scripts use content hashes so returning browsers pick up updated assets. Build with SITE_URL when the production address is decided. This local build does not update the separate DuckDNS deployment.


For advertising, link to the page that answers the advert's specific promise. Trial-diving and certification adverts have separate course anchors. Scubility leads to the inclusive training section. First-aid enquiries start from the appropriate programme; rentals lead to the rate table; model-specific equipment enquiries start on the product page. The destination mapping is recorded in content/site-review.json. No advertising campaign or tracking script has been added.

The travel source contained flags and venue logos rather than trip photographs. These are no longer presented as a photo gallery. The page now communicates the dated trip and event archive; achievement galleries retain their original images. Approved real trip photographs can be added later.
