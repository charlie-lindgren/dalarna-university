import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"

// Explorer-sortering: hubb-/indexsidor (folderns översiktssida) hamnar först
// bland filerna inom samma mapp; därefter mappar (för konsistens med Quartz
// default är mappar redan först bland folder/file-jämförelsen), och slutligen
// filer alfabetiskt. Hubbar identifieras på den interna ``MOC``-taggen — namnen
// är numera rena (t.ex. "Datateknik", "IIT Analys"), så filnamns-suffixet
// "MOC" finns inte längre att sortera på.
const mocFirstSortFn = (a: any, b: any) => {
  // Behåll Quartz defaultbeteende mellan folder/file: mappar först.
  if (!a.isFolder && b.isFolder) return 1
  if (a.isFolder && !b.isFolder) return -1
  // Inom samma kategori (båda är filer eller båda är mappar): hubbar
  // (MOC-taggade) sorteras före allt annat.
  const aIsHub = !!a.data?.tags?.includes("MOC")
  const bIsHub = !!b.data?.tags?.includes("MOC")
  if (aIsHub && !bIsHub) return -1
  if (!aIsHub && bIsHub) return 1
  return a.displayName.localeCompare(b.displayName, undefined, {
    numeric: true,
    sensitivity: "base",
  })
}

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [],
  afterBody: [],
  footer: Component.Footer({
    links: {
      GitHub: "https://github.com/jackyzha0/quartz",
      "Discord Community": "https://discord.gg/cRFFHYye7t",
    },
  }),
}

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.ConditionalRender({
      component: Component.Breadcrumbs(),
      condition: (page) => page.fileData.slug !== "index",
    }),
    Component.ArticleTitle(),
    Component.ContentMeta(),
    Component.TagList(),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
        { Component: Component.ReaderMode() },
      ],
    }),
    Component.Explorer({ sortFn: mocFirstSortFn }),
  ],
  right: [
    Component.Graph({
      localGraph: {
        showTags: false,
        depth: 2,
        linkDistance: 50,
        repelForce: 1,
        fontSize: 1,
      },
      globalGraph: {
        showTags: false,
        depth: -1,
        scale: 0.6,
        linkDistance: 85,
        repelForce: 1.4,
        centerForce: 0.2,
        fontSize: 0.5,
        opacityScale: 1.5,
        enableRadial: false,
        selfContainedClusters: true,
      },
    }),
    Component.DesktopOnly(Component.TableOfContents()),
    Component.Backlinks(),
  ],
}

// components for pages that display lists of pages  (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.Breadcrumbs(), Component.ArticleTitle(), Component.ContentMeta()],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
      ],
    }),
    Component.Explorer({ sortFn: mocFirstSortFn }),
  ],
  right: [],
}
