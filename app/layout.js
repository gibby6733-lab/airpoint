import "./globals.css";

export const metadata = {
  title: "AirPoint — Dew Point & Humidity Calculators",
  description:
    "Free dew point, humidity, relative humidity, and condensation calculators.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <script
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3425475947280138"
          crossOrigin="anonymous"
        ></script>
      </head>

      <body>{children}</body>
    </html>
  );
}