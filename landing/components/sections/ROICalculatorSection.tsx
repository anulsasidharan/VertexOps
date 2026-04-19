"use client";
import { useState, useMemo } from "react";
import { Calculator, TrendingUp, DollarSign, Clock } from "lucide-react";
import { AnimateOnScroll } from "../ui/AnimateOnScroll";

const SLIDER = (label: string, min: number, max: number, step: number, value: number, onChange: (v: number) => void, format: (v: number) => string) => (
  <div>
    <div className="flex justify-between items-center mb-2">
      <label className="text-sm font-medium text-gray-700">{label}</label>
      <span className="text-sm font-bold text-primary-600">{format(value)}</span>
    </div>
    <input
      type="range"
      min={min}
      max={max}
      step={step}
      value={value}
      onChange={(e) => onChange(Number(e.target.value))}
      className="w-full h-2 bg-gray-200 rounded-full appearance-none cursor-pointer accent-primary-500"
    />
    <div className="flex justify-between text-xs text-gray-400 mt-1">
      <span>{format(min)}</span>
      <span>{format(max)}</span>
    </div>
  </div>
);

export function ROICalculatorSection() {
  const [cloudSpend, setCloudSpend] = useState(50000);
  const [incidents, setIncidents] = useState(20);
  const [teamSize, setTeamSize] = useState(10);
  const [accounts, setAccounts] = useState(3);

  const results = useMemo(() => {
    const costSavings = cloudSpend * 0.40;
    const engineerHourlyRate = 150;
    const incidentHoursReduced = incidents * 2.5 * 0.67;
    const incidentSavings = incidentHoursReduced * engineerHourlyRate;
    const toolingConsolidation = accounts * 800;
    const totalMonthlySavings = costSavings + incidentSavings + toolingConsolidation;
    const annualSavings = totalMonthlySavings * 12;
    const mttrReduction = 67;
    const automationCoverage = Math.min(95, 60 + accounts * 5 + Math.floor(incidents / 4));

    return {
      costSavings: Math.round(costSavings),
      incidentSavings: Math.round(incidentSavings),
      toolingConsolidation: Math.round(toolingConsolidation),
      totalMonthlySavings: Math.round(totalMonthlySavings),
      annualSavings: Math.round(annualSavings),
      mttrReduction,
      automationCoverage,
      paybackDays: Math.round((1999 / totalMonthlySavings) * 30),
    };
  }, [cloudSpend, incidents, teamSize, accounts]);

  const fmt = (v: number) => v >= 1000 ? `$${(v / 1000).toFixed(0)}K` : `$${v}`;

  return (
    <section id="roi-calculator" className="section-padding bg-white">
      <div className="container-max">
        <AnimateOnScroll className="text-center mb-14">
          <div className="section-label">
            <span className="w-1.5 h-1.5 rounded-full bg-success" />
            ROI Calculator
          </div>
          <h2 className="section-heading mb-4">
            Calculate Your{" "}
            <span className="gradient-text">Potential Savings</span>
          </h2>
          <p className="section-subheading mx-auto">
            Input your current numbers and see how much VertexOps can save
            your team every month.
          </p>
        </AnimateOnScroll>

        <AnimateOnScroll>
          <div className="grid lg:grid-cols-2 gap-12">
            {/* Inputs */}
            <div className="card-base p-8 space-y-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
                  <Calculator className="w-5 h-5 text-primary-500" />
                </div>
                <div>
                  <div className="text-lg font-bold text-gray-900">Your Inputs</div>
                  <div className="text-sm text-gray-500">Drag to adjust values</div>
                </div>
              </div>

              {SLIDER("Monthly Cloud Spend", 5000, 500000, 5000, cloudSpend, setCloudSpend, (v) => `$${(v / 1000).toFixed(0)}K/mo`)}
              {SLIDER("Incidents Per Month", 5, 100, 5, incidents, setIncidents, (v) => `${v} incidents`)}
              {SLIDER("Engineering Team Size", 3, 100, 1, teamSize, setTeamSize, (v) => `${v} engineers`)}
              {SLIDER("Cloud Accounts / Projects", 1, 20, 1, accounts, setAccounts, (v) => `${v} accounts`)}
            </div>

            {/* Results */}
            <div className="space-y-4">
              {/* Big number */}
              <div className="bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl p-8 text-white">
                <div className="text-sm font-semibold text-primary-200 mb-2 uppercase tracking-wide">
                  Estimated Monthly Savings
                </div>
                <div className="text-5xl font-bold mb-1">
                  {fmt(results.totalMonthlySavings)}
                </div>
                <div className="text-primary-200 text-sm">
                  {fmt(results.annualSavings)}/year · ROI positive in ~{results.paybackDays} days
                </div>
              </div>

              {/* Breakdown */}
              <div className="card-base p-6 space-y-4">
                <div className="text-sm font-semibold text-gray-700 mb-4">Savings Breakdown</div>
                {[
                  { icon: DollarSign, label: "Cloud cost optimization (40%)", value: results.costSavings, color: "text-success" },
                  { icon: Clock, label: "Faster incident resolution (67%)", value: results.incidentSavings, color: "text-primary-500" },
                  { icon: TrendingUp, label: "Tooling consolidation", value: results.toolingConsolidation, color: "text-secondary-500" },
                ].map(({ icon: Icon, label, value, color }) => (
                  <div key={label} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                    <div className="flex items-center gap-3">
                      <Icon className={`w-4 h-4 ${color}`} />
                      <span className="text-sm text-gray-600">{label}</span>
                    </div>
                    <span className={`text-sm font-bold ${color}`}>{fmt(value)}/mo</span>
                  </div>
                ))}
              </div>

              {/* Operational metrics */}
              <div className="grid grid-cols-2 gap-4">
                {[
                  { label: "MTTR Reduction", value: `${results.mttrReduction}%`, icon: Clock },
                  { label: "Automation Coverage", value: `${results.automationCoverage}%`, icon: TrendingUp },
                ].map(({ label, value, icon: Icon }) => (
                  <div key={label} className="card-base p-5 text-center">
                    <Icon className="w-5 h-5 text-primary-500 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-gray-900 mb-1">{value}</div>
                    <div className="text-xs text-gray-500 font-medium">{label}</div>
                  </div>
                ))}
              </div>

              <a href="#pricing" className="btn-primary w-full justify-center py-3.5 text-base">
                Get Your Full ROI Report
              </a>
            </div>
          </div>
        </AnimateOnScroll>
      </div>
    </section>
  );
}
