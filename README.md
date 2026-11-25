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


## Shared icons and colour system

`design.py` supplies local decorative SVG icons across every generated page. The shared header/footer, contact methods, page covers, offer cards, category labels and enquiry actions use the same icon shapes and spacing. Ocean blue identifies diving, sage identifies inclusive diving, coral identifies first aid, sand identifies equipment and lavender identifies the school. The core teal identity and original logo are retained.

The 19 category illustrations were created with the built-in image generator in generate mode, in a consistent teal, seafoam and ivory style. Transparent, optimized WebP assets are in `public/assets/illustrated-icons/`; original PNGs and the exact prompts are preserved in `artwork/originals/` and `artwork/prompts.json`. The same artwork family is used for large categories, smaller service cards, navigation and category chips. These illustrations describe services, rather than replacing real instructor portraits or product photography.

Functional interface symbols such as phone, email, search and enquiry use local Phosphor SVGs, pinned to commit `2b75f3ad12b420c9504ef05df8d2564a28f8500e`. Their MIT license is included at `public/licenses/phosphor-icons.txt`, with provenance in `artwork/ui-icons.json`. The WhatsApp brand path is from the Simple Icons repository, stored at `public/assets/whatsapp.svg` (source https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/whatsapp.svg). No external icon script or font is loaded. Decorative icons are hidden from assistive technology and remain paired with visible labels. Navigation uses clear teal links and open editorial rows, with buttons reserved for primary actions. Hover and focus treatments remain visible.

Section introductions use centered alignment and constrained reading widths. Information and service destinations use open editorial rows with grouped copy and clear links. Longer descriptions, forms and product specifications retain a consistent left edge. The original logo, instructor portraits, product images and homepage video remain in use.

## Imported text formatting

`typography.py` groups source line fragments, formats product features as lists and splits long paragraphs at sentence boundaries. German abbreviations and the supplied wording are preserved. Product titles and prices already displayed in the page header are not repeated in the extra-description panel. The catalogue JSON remains unchanged.

The legal page groups address lines and contact fields, uses real lists, and gives long text a restrained reading width and clear heading hierarchy. This is a formatting update to the copied source, not a legal-content review. Empty source headings with no accompanying information are omitted.

Shared row spacing keeps titles, descriptions and actions together without artificial blank title rows. Product imagery, reviews, pricing decisions and forms retain purposeful bounded surfaces. Reading copy remains left aligned at a minimum 16px, with 17px legal text on desktop.

## Enquiry and team layout

The enquiry page has a compact cover and a single form card with conditional course/product and period fields. Buying and rental are separate topics. Existing `thema=Ausrüstung und Verleih` links map to buying when a product is supplied, otherwise rental. Course and product names are preserved in structured message drafts; changing topic preserves the visitor's message. WhatsApp and email open drafts for the visitor to review and send. No server submission was added.

The homepage team introduction is a standalone section before the Google reviews. The team page centers the founder above four aligned profiles on desktop, two columns on tablet and one on narrow mobile screens. Original portraits and qualifications are retained.

## Sitewide editorial design

`src/editorial.css` is the shared final layout layer, loaded after `main.css` on every generated page with a content hash. It implements the chosen Open editorial direction: transparent information/service rows, thin rules, readable text groups and clear destinations. The school directory uses a reusable `editorial-row` structure with one leading illustration and separate action links. Homepage visitor goals, equipment service links, first-aid programmes, reference panels, shop browsing and legal navigation use the same principles.

The homepage trip highlight uses an existing approved lake image with a dark teal overlay. Product photographs, customer reviews, price decisions and the enquiry form retain bounded surfaces where those help understanding. The real logo, instructor portraits, catalogue data, copied page text and destinations are retained.

Validation for this pass: all 131 pages loaded the layout layer and retained identical main-page copy; local links/media/anchors/forms passed; all pages fit at 360, 768 and 1440 pixels without horizontal overflow or broken images. Representative pages were visually reviewed, and catalogue search, mobile menu, product expansion and prefilled enquiries were checked.
