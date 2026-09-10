import type { Metadata } from "next";
import { Source_Sans_3 } from "next/font/google";
import { AuthProvider } from "@/hooks/useAuth";
import "./globals.css";

const sourceSans = Source_Sans_3({
  subsets: ["latin"],
  variable: "--font-source-sans",
});

export const metadata: Metadata = {
  title: "CareHaven AI",
  description:
    "An intelligent humanitarian aid and donation platform connecting cases, donors, and review teams.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${sourceSans.variable} font-sans`}>
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-white focus:px-3 focus:py-2"
        >
          Skip to content
        </a>
        <AuthProvider>
          <div id="main-content">{children}</div>
        </AuthProvider>
      </body>
    </html>
  );
}
