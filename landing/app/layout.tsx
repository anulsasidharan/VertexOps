import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://orionvexa.ca"),
  title: "VertexOps — AI-Powered Infrastructure Operations & DevOps Intelligence",
  description:
    "Transform multi-cloud chaos into clarity with VertexOps. AI-powered monitoring, automated incident response, and cost optimization for GCP, AWS, and Azure. Reduce MTTR by 67% and cut costs by 40%.",
  keywords:
    "DevOps automation, infrastructure monitoring, multi-cloud management, FinOps, AI incident response, GCP monitoring, AWS monitoring, SRE tools, platform engineering",
  openGraph: {
    title: "VertexOps — AI-Powered Infrastructure Operations",
    description:
      "AI-powered monitoring, incident response, and cost optimization for modern DevOps teams",
    url: "https://orionvexa.ca/vertexops",
    siteName: "VertexOps",
    type: "website",
    images: [{ url: "/og-image.png", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "VertexOps — AI-Powered DevOps Intelligence",
    description:
      "Reduce MTTR by 67% and cut costs by 40% with AI-powered infrastructure operations",
    images: ["/og-image.png"],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
      </head>
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
