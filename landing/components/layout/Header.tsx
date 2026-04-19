"use client";
import { useState, useEffect } from "react";
import { Menu, X, Zap } from "lucide-react";

const NAV_LINKS = [
  { label: "Product", href: "#features" },
  { label: "How It Works", href: "#how-it-works" },
  { label: "Integrations", href: "#integrations" },
  { label: "Pricing", href: "#pricing" },
  { label: "Docs", href: "#api" },
];

export function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-white/95 backdrop-blur-md border-b border-gray-100 shadow-sm"
          : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <a href="#" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center shadow-sm group-hover:bg-primary-600 transition-colors">
            <Zap className="w-4 h-4 text-white fill-white" />
          </div>
          <span className="text-lg font-bold text-gray-900">
            Vertex<span className="text-primary-500">Ops</span>
          </span>
        </a>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-8">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className={`text-sm font-medium transition-colors ${
                scrolled
                  ? "text-gray-600 hover:text-primary-500"
                  : "text-gray-700 hover:text-primary-500"
              }`}
            >
              {link.label}
            </a>
          ))}
        </nav>

        {/* CTA buttons */}
        <div className="hidden md:flex items-center gap-3">
          <a
            href="#"
            className="text-sm font-medium text-gray-600 hover:text-primary-500 transition-colors px-3 py-2"
          >
            Log in
          </a>
          <a href="#pricing" className="btn-primary text-sm px-4 py-2 rounded-lg">
            Get Started
          </a>
        </div>

        {/* Mobile hamburger */}
        <button
          className="md:hidden p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle menu"
        >
          {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden bg-white border-t border-gray-100 px-6 py-4 space-y-1">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => setMenuOpen(false)}
              className="block px-3 py-2.5 text-sm font-medium text-gray-600 hover:text-primary-500 hover:bg-primary-50 rounded-lg transition-colors"
            >
              {link.label}
            </a>
          ))}
          <div className="pt-3 border-t border-gray-100 flex flex-col gap-2">
            <a href="#" className="btn-secondary text-sm py-2.5 rounded-lg justify-center">
              Log in
            </a>
            <a href="#pricing" className="btn-primary text-sm py-2.5 rounded-lg justify-center">
              Get Started Free
            </a>
          </div>
        </div>
      )}
    </header>
  );
}
