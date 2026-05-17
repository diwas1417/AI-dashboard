import { useState } from "react";
import {
  uploadMarketTrendPdf,
  uploadSuburbPdf,
  getFullMediaUrl,
} from "./api";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("market");

  const [marketFile, setMarketFile] = useState(null);
  const [suburbFile, setSuburbFile] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [modalOpen, setModalOpen] = useState(false);
  const [outputUrl, setOutputUrl] = useState("");
  const [outputType, setOutputType] = useState("");
  const [outputTitle, setOutputTitle] = useState("");

  const isMarketTab = activeTab === "market";

  const currentFile = isMarketTab ? marketFile : suburbFile;

  function handleTabChange(tabName) {
    setActiveTab(tabName);
    setError("");
  }

  function handleFileChange(event) {
    const file = event.target.files[0];

    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Please upload PDF file only.");
      return;
    }

    setError("");

    if (isMarketTab) {
      setMarketFile(file);
    } else {
      setSuburbFile(file);
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!currentFile) {
      setError("Please upload a PDF file first.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      let data;

      if (isMarketTab) {
        data = await uploadMarketTrendPdf(currentFile);
      } else {
        data = await uploadSuburbPdf(currentFile);
      }

      /*
        Backend may return different key names.
        So we check multiple possible names.
      */
      const returnedUrl =
        data.chart_url ||
        data.graph_url ||
        data.image_url ||
        data.pdf_url ||
        data.edited_pdf_url ||
        data.file_url ||
        data.output_url;

      const fullUrl = getFullMediaUrl(returnedUrl);

      setOutputUrl(fullUrl);

      if (isMarketTab) {
        setOutputType("image");
        setOutputTitle("Generated Market Trend Graph");
      } else {
        setOutputType("pdf");
        setOutputTitle("Edited Suburb Statistics PDF");
      }

      setModalOpen(true);
    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.error ||
          error.response?.data?.detail ||
          "Something went wrong. Please check your backend API."
      );
    } finally {
      setLoading(false);
    }
  }

  function removeFile() {
    if (isMarketTab) {
      setMarketFile(null);
    } else {
      setSuburbFile(null);
    }

    setError("");
  }

  function closeModal() {
    setModalOpen(false);
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="logo-box">
          <div className="logo">AI</div>
          <div>
            <h2>AI Dashboard</h2>
            <p>Property report tools</p>
          </div>
        </div>

        <nav className="nav-menu">
          <button
            className={activeTab === "market" ? "nav-btn active" : "nav-btn"}
            onClick={() => handleTabChange("market")}
          >
            📈 Market Trend Graph
          </button>

          <button
            className={activeTab === "suburb" ? "nav-btn active" : "nav-btn"}
            onClick={() => handleTabChange("suburb")}
          >
            📄 Suburb PDF Editor
          </button>
        </nav>

        <div className="sidebar-footer">
          <p>Workflow</p>
          <span>Upload PDF → Generate → Preview → Download</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="page-header">
          <div>
            <p className="small-title">
              {isMarketTab
                ? "CMA / CoreLogic / Cotality Report"
                : "Suburb Statistics Report"}
            </p>

            <h1>
              {isMarketTab
                ? "Market Trend Graph"
                : "Suburb Statistics PDF Editor"}
            </h1>
          </div>

          <span className="api-status">Django API</span>
        </header>

        <section className="upload-card">
          <div className="upload-info">
            <p className="section-label">
              {isMarketTab ? "Graph Generator" : "PDF Editor"}
            </p>

            <h2>
              {isMarketTab
                ? "Upload CMA report and generate graph"
                : "Upload suburb report and get edited PDF"}
            </h2>

            <p>
              {isMarketTab
                ? "This tool will upload the report to Django, process the Long Term Market Trends section, and show the generated graph in a preview modal."
                : "This tool will upload the suburb statistics report, edit the PDF output, and show the edited PDF in a preview modal."}
            </p>
          </div>

          <form className="upload-form" onSubmit={handleSubmit}>
            <label className="file-upload-box">
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                disabled={loading}
              />

              <span className="upload-icon">⬆</span>

              <strong>
                {isMarketTab
                  ? "Upload CMA report PDF"
                  : "Upload suburb statistics PDF"}
              </strong>

              <small>Click here to select PDF file</small>
            </label>

            {currentFile && (
              <div className="selected-file">
                <div>
                  <strong>{currentFile.name}</strong>
                  <span>{formatFileSize(currentFile.size)}</span>
                </div>

                <button type="button" onClick={removeFile} disabled={loading}>
                  Remove
                </button>
              </div>
            )}

            {error && <div className="error-message">{error}</div>}

            <button className="submit-btn" type="submit" disabled={loading}>
              {loading
                ? "Processing..."
                : isMarketTab
                ? "Generate Graph"
                : "Edit PDF"}
            </button>
          </form>
        </section>

        <section className="steps-grid">
          <div className="step-card">
            <h3>1. Upload</h3>
            <p>Select the PDF report from your computer.</p>
          </div>

          <div className="step-card">
            <h3>2. Process</h3>
            <p>The file is sent to your Django backend API.</p>
          </div>

          <div className="step-card">
            <h3>3. Preview</h3>
            <p>The output opens in a modal with download option.</p>
          </div>
        </section>
      </main>

      {modalOpen && (
        <OutputModal
          title={outputTitle}
          url={outputUrl}
          type={outputType}
          onClose={closeModal}
        />
      )}
    </div>
  );
}

function OutputModal({ title, url, type, onClose }) {
  return (
    <div className="modal-overlay">
      <div className="modal-box">
        <div className="modal-header">
          <div>
            <p className="small-title">Output Preview</p>
            <h2>{title}</h2>
          </div>

          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="modal-body">
          {!url && (
            <div className="no-preview">
              <h3>No output URL received</h3>
              <p>
                Backend response was successful, but no chart or PDF URL was
                found. Check your Django response key.
              </p>
            </div>
          )}

          {url && type === "image" && (
            <img className="image-preview" src={url} alt="Generated output" />
          )}

          {url && type === "pdf" && (
            <iframe className="pdf-preview" src={url} title="PDF Preview" />
          )}
        </div>

        <div className="modal-footer">
          {url && (
            <a
              href={url}
              download
              target="_blank"
              rel="noreferrer"
              className="download-btn"
            >
              Download Output
            </a>
          )}

          <button className="close-btn" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

function formatFileSize(bytes) {
  if (!bytes) return "0 KB";

  const sizeInKb = bytes / 1024;

  if (sizeInKb < 1024) {
    return `${sizeInKb.toFixed(1)} KB`;
  }

  return `${(sizeInKb / 1024).toFixed(2)} MB`;
}

export default App;