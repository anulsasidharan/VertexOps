import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { HeroSection } from "@/components/sections/HeroSection";
import { LogoCloud } from "@/components/sections/LogoCloud";
import { ProblemSection } from "@/components/sections/ProblemSection";
import { FeaturesSection } from "@/components/sections/FeaturesSection";
import { HowItWorksSection } from "@/components/sections/HowItWorksSection";
import { UseCasesSection } from "@/components/sections/UseCasesSection";
import { IntegrationsSection } from "@/components/sections/IntegrationsSection";
import { TechSpecsSection } from "@/components/sections/TechSpecsSection";
import { APISection } from "@/components/sections/APISection";
import { ROICalculatorSection } from "@/components/sections/ROICalculatorSection";
import { PricingSection } from "@/components/sections/PricingSection";
import { SecuritySection } from "@/components/sections/SecuritySection";
import { TestimonialsSection } from "@/components/sections/TestimonialsSection";
import { FAQSection } from "@/components/sections/FAQSection";
import { FinalCTASection } from "@/components/sections/FinalCTASection";

export default function Home() {
  return (
    <>
      <Header />
      <main>
        <HeroSection />
        <LogoCloud />
        <ProblemSection />
        <FeaturesSection />
        <HowItWorksSection />
        <UseCasesSection />
        <IntegrationsSection />
        <TechSpecsSection />
        <APISection />
        <ROICalculatorSection />
        <PricingSection />
        <SecuritySection />
        <TestimonialsSection />
        <FAQSection />
        <FinalCTASection />
      </main>
      <Footer />
    </>
  );
}
