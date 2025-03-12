import React, { useState } from "react";
import { motion } from "framer-motion";

// OPTIONAL: If you need a utility function similar to 'cn' (className merging),
// either remove these or define your own function:
function cn(...classes) {
  return classes.filter(Boolean).join(" ");
}

/*
  Simple Animated Transition (previously AnimatedTransition.tsx).
  Removed TypeScript types and uses plain JS now.
*/
function AnimatedTransition({
  children,
  className,
  animationType = "fade",
  duration = 0.5,
  delay = 0,
}) {
  const variants = {
    fade: {
      hidden: { opacity: 0 },
      visible: { opacity: 1 },
    },
    "slide-up": {
      hidden: { y: 20, opacity: 0 },
      visible: { y: 0, opacity: 1 },
    },
    "slide-down": {
      hidden: { y: -20, opacity: 0 },
      visible: { y: 0, opacity: 1 },
    },
    scale: {
      hidden: { scale: 0.95, opacity: 0 },
      visible: { scale: 1, opacity: 1 },
    },
  };

  return (
    <motion.div
      className={cn(className)}
      initial="hidden"
      animate="visible"
      exit="hidden"
      variants={variants[animationType]}
      transition={{
        duration,
        delay,
        ease: [0.25, 0.1, 0.25, 1.0],
      }}
    >
      {children}
    </motion.div>
  );
}

/*
  Main Synthesizer component.
  - Uses a black "lightning/space" background
  - Puts the data form in the center
  - Underneath, we show a "Results" block if data is generated
*/
export default function Synthesizer() {
  // -- STATE FOR FORM --
  const [datasetSize, setDatasetSize] = useState(100);
  const [transactionType, setTransactionType] = useState("all");
  const [timeRange, setTimeRange] = useState("last-month");
  const [outlierPercentage, setOutlierPercentage] = useState(5);
  const [includeMetadata, setIncludeMetadata] = useState(true);
  const [categoryDistribution, setCategoryDistribution] = useState("");
  const [minAmount, setMinAmount] = useState("");
  const [maxAmount, setMaxAmount] = useState("");

  // -- STATE FOR RESULTS --
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedData, setGeneratedData] = useState(null);

  // -- HANDLE DATASET GENERATION --
  const handleGenerate = () => {
    setIsGenerating(true);

    // Simulate data generation delay
    setTimeout(() => {
      // Sample synthetic dataset: real logic can vary
      const data = [];
      for (let i = 0; i < datasetSize; i++) {
        data.push({
          id: i + 1,
          type: transactionType,
          amount: randomInRange(
            parseFloat(minAmount) || 10,
            parseFloat(maxAmount) || 1000
          ),
          timeRange: timeRange,
          metadata: includeMetadata ? { info: "sample" } : null,
        });
      }
      setGeneratedData(data);
      setIsGenerating(false);
    }, 1500);
  };

  // Random helper for amounts
  function randomInRange(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  // -- HANDLE DOWNLOAD/CLIPBOARD --
  const handleCopyToClipboard = () => {
    if (!generatedData) return;
    navigator.clipboard.writeText(JSON.stringify(generatedData, null, 2));
    alert("Data copied to clipboard!");
  };

  const handleDownload = () => {
    if (!generatedData) return;
    const jsonString = JSON.stringify(generatedData, null, 2);
    const blob = new Blob([jsonString], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "synthetic_transactions.json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    alert("Downloaded JSON file!");
  };

  // -- RESET FORM --
  const handleReset = () => {
    setDatasetSize(100);
    setTransactionType("all");
    setTimeRange("last-month");
    setOutlierPercentage(5);
    setIncludeMetadata(true);
    setCategoryDistribution("");
    setMinAmount("");
    setMaxAmount("");
    setGeneratedData(null);
  };

  return (
    <div
      // Full-screen, black background, lightning overlay
      style={{
        minHeight: "100vh",
        backgroundColor: "#000000",
        backgroundImage: "url('/path-to-your-lightning-image.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        color: "#FFFFFF",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "40px 20px",
      }}
    >
      <AnimatedTransition animationType="fade" duration={1} className="w-full">
        {/* Title Section in Middle */}
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <h1 style={{ fontSize: "2rem", fontWeight: "bold", marginBottom: 8 }}>
            Transaction Data Synthesizer
          </h1>
          <p style={{ maxWidth: 600, margin: "0 auto", color: "#B0B0B0" }}>
            Generate realistic, synthetic transaction datasets with a single click.
            Configure your parameters below to create custom datasets.
          </p>
        </div>

        {/* MAIN FORM (Single Panel) */}
        <div
          style={{
            maxWidth: 800,
            width: "100%",
            margin: "0 auto",
            backgroundColor: "rgba(0,0,0,0.6)",
            borderRadius: 8,
            padding: 20,
            border: "1px solid #444",
          }}
        >
          {/* Basic Parameters */}
          <div style={{ marginBottom: "1rem" }}>
            <label>
              <span>Dataset Size:</span> {datasetSize}
            </label>
            <input
              type="range"
              min={10}
              max={1000}
              step={10}
              value={datasetSize}
              onChange={(e) => setDatasetSize(parseInt(e.target.value, 10))}
              style={{ width: "100%", margin: "8px 0" }}
            />
          </div>

          <div style={{ marginBottom: "1rem" }}>
            <label style={{ display: "block", marginBottom: 4 }}>
              Transaction Type:
            </label>
            <select
              value={transactionType}
              onChange={(e) => setTransactionType(e.target.value)}
              style={{ width: "100%", padding: 4 }}
            >
              <option value="all">All Transactions</option>
              <option value="credit">Credit Transactions</option>
              <option value="debit">Debit Transactions</option>
              <option value="transfer">Transfers Only</option>
              <option value="recurring">Recurring Payments</option>
            </select>
          </div>

          <div style={{ marginBottom: "1rem" }}>
            <label style={{ display: "block", marginBottom: 4 }}>
              Time Range:
            </label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              style={{ width: "100%", padding: 4 }}
            >
              <option value="last-week">Last Week</option>
              <option value="last-month">Last Month</option>
              <option value="last-quarter">Last Quarter</option>
              <option value="last-year">Last Year</option>
              <option value="custom">Custom Range</option>
            </select>
          </div>

          {/* Advanced Parameters */}
          <div style={{ marginBottom: "1rem" }}>
            <label>
              <span>Outlier Percentage:</span> {outlierPercentage}%
            </label>
            <input
              type="range"
              min={0}
              max={20}
              step={1}
              value={outlierPercentage}
              onChange={(e) => setOutlierPercentage(parseInt(e.target.value, 10))}
              style={{ width: "100%", margin: "8px 0" }}
            />
          </div>

          <div style={{ marginBottom: "1rem" }}>
            <label style={{ display: "block", marginBottom: 4 }}>
              Include Metadata:
            </label>
            <input
              type="checkbox"
              checked={includeMetadata}
              onChange={(e) => setIncludeMetadata(e.target.checked)}
            />
          </div>

          {/* Custom Parameters */}
          <div style={{ marginBottom: "1rem" }}>
            <label style={{ display: "block", marginBottom: 4 }}>
              Category Distribution:
            </label>
            <input
              type="text"
              placeholder="e.g., food:30,transport:20"
              value={categoryDistribution}
              onChange={(e) => setCategoryDistribution(e.target.value)}
              style={{ width: "100%", padding: 6 }}
            />
          </div>

          <div style={{ marginBottom: "1rem" }}>
            <label style={{ display: "block", marginBottom: 4 }}>
              Transaction Amount Range:
            </label>
            <div style={{ display: "flex", gap: 8 }}>
              <input
                type="number"
                placeholder="Min amount"
                value={minAmount}
                onChange={(e) => setMinAmount(e.target.value)}
                style={{ flex: 1, padding: 6 }}
              />
              <input
                type="number"
                placeholder="Max amount"
                value={maxAmount}
                onChange={(e) => setMaxAmount(e.target.value)}
                style={{ flex: 1, padding: 6 }}
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}>
            <button
              onClick={handleReset}
              disabled={isGenerating}
              style={{
                padding: "6px 12px",
                border: "1px solid #888",
                background: "transparent",
                color: "#FFF",
                cursor: isGenerating ? "not-allowed" : "pointer",
              }}
            >
              Reset
            </button>

            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              style={{
                padding: "6px 12px",
                backgroundColor: "#5e62c7",
                border: "none",
                color: "#FFF",
                cursor: isGenerating ? "not-allowed" : "pointer",
              }}
            >
              {isGenerating ? "Generating..." : "Generate Dataset"}
            </button>
          </div>
        </div>

        {/* RESULTS DISPLAY SECTION */}
        {isGenerating && (
          <div style={{ textAlign: "center", marginTop: "2rem" }}>
            <p>Generating your dataset, please wait...</p>
          </div>
        )}

        {generatedData && (
          <AnimatedTransition animationType="scale" className="mt-8">
            <div
              style={{
                maxWidth: 900,
                width: "100%",
                margin: "2rem auto 0",
                backgroundColor: "rgba(0,0,0,0.6)",
                borderRadius: 8,
                padding: 20,
                border: "1px solid #444",
              }}
            >
              <h2 style={{ fontSize: "1.5rem", marginBottom: 8 }}>
                Generated Dataset
              </h2>
              <p style={{ color: "#AAA", marginBottom: 16 }}>
                {generatedData.length} synthetic transactions
              </p>

              {/* Actions: Copy & Download */}
              <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
                <button
                  onClick={handleCopyToClipboard}
                  style={{
                    padding: "6px 12px",
                    border: "1px solid #888",
                    background: "transparent",
                    color: "#FFF",
                  }}
                >
                  Copy JSON
                </button>
                <button
                  onClick={handleDownload}
                  style={{
                    padding: "6px 12px",
                    backgroundColor: "#5e62c7",
                    border: "none",
                    color: "#FFF",
                  }}
                >
                  Download JSON
                </button>
              </div>

              {/* Show just a sample of the data in JSON */}
              <div
                style={{
                  backgroundColor: "#1E1E1E",
                  color: "#FFFFFF",
                  padding: 12,
                  borderRadius: 4,
                  maxHeight: 300,
                  overflow: "auto",
                  fontSize: "0.85rem",
                }}
              >
                <pre style={{ margin: 0 }}>
                  {JSON.stringify(generatedData.slice(0, 10), null, 2)}
                </pre>
                {generatedData.length > 10 && (
                  <p style={{ marginTop: 8, color: "#888" }}>
                    Showing 10 of {generatedData.length} records
                  </p>
                )}
              </div>

              <p style={{ fontSize: "0.75rem", color: "#BBB", marginTop: 16 }}>
                * This data is synthesized; it does not represent real user
                transactions.
              </p>
            </div>
          </AnimatedTransition>
        )}
      </AnimatedTransition>
    </div>
  );
}
