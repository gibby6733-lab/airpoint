export default function robots() {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
    },
    sitemap: "https://airpoint.vercel.app/sitemap.xml",
  };
}