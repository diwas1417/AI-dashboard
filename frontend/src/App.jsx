import { useState } from "react";
import {
    uploadMarketTrendPdf,
    uploadSuburbPdf,
    getFullMediaUrl,
    getAmenityScore,
    loginUser,
    registerUser,
    logoutUser,
} from "./api";
import "./App.css";

function App() {
    const [activeTab, setActiveTab] = useState("market");

    const [marketFile, setMarketFile] = useState(null);
    const [suburbFile, setSuburbFile] = useState(null);

    const [propertyAddress, setPropertyAddress] = useState("");
    const [amenityData, setAmenityData] = useState(null);
    const [amenityLoading, setAmenityLoading] = useState(false);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const [modalOpen, setModalOpen] = useState(false);
    const [outputUrl, setOutputUrl] = useState("");
    const [outputType, setOutputType] = useState("");
    const [outputTitle, setOutputTitle] = useState("");

    const [authUser, setAuthUser] = useState(() => {
        const savedUser = localStorage.getItem("authUser");
        return savedUser ? JSON.parse(savedUser) : null;
    });

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

            console.log("PDF tool response:", data);

            let returnedUrl;

            if (isMarketTab) {
                returnedUrl =
                    data.chart_url ||
                    data.graph_url ||
                    data.image_url ||
                    data.output_url;
            } else {
                returnedUrl =
                    data.edited_pdf_url ||
                    data.pdf_url ||
                    data.file_url ||
                    data.output_url;
            }

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

            if (error.response?.status === 401) {
                setError("Please login again. Your session may have expired.");
            } else {
                setError(
                    error.response?.data?.error ||
                        error.response?.data?.detail ||
                        "Something went wrong. Please try again."
                );
            }
        } finally {
            setLoading(false);
        }
    }

    async function handleAmenitySearch(event) {
        event.preventDefault();

        const cleanAddress = propertyAddress.trim();

        if (!cleanAddress) {
            setError("Please enter a property address.");
            return;
        }

        setError("");
        setAmenityLoading(true);
        setAmenityData(null);

        try {
            const data = await getAmenityScore(cleanAddress);
            console.log("Amenity score response:", data);
            setAmenityData(data);
        } catch (error) {
            console.error(error);

            if (error.response?.status === 401) {
                setError("Please login again. Your session may have expired.");
            } else {
                setError(
                    error.response?.data?.error ||
                        error.response?.data?.detail ||
                        "Something went wrong while generating the amenity score."
                );
            }
        } finally {
            setAmenityLoading(false);
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

    async function handleLogout() {
        try {
            await logoutUser();
        } catch (error) {
            console.error(error);
        } finally {
            localStorage.removeItem("authToken");
            localStorage.removeItem("authUser");
            setAuthUser(null);
            setMarketFile(null);
            setSuburbFile(null);
            setAmenityData(null);
            setError("");
        }
    }

    if (!authUser) {
        return <AuthPage onAuthSuccess={setAuthUser} />;
    }

    return (
        <div className="app">
            <aside className="sidebar">
                <div className="logo-box">
                    <div className="logo">AI</div>
                    <div>
                        <h2>Property Tools</h2>
                        <p>Investment research workspace</p>
                    </div>
                </div>

                <nav className="nav-menu">
                    <button
                        className={`nav-btn ${
                            activeTab === "market" ? "active" : ""
                        }`}
                        onClick={() => handleTabChange("market")}
                    >
                        Market Trend Graph
                    </button>

                    <button
                        className={`nav-btn ${
                            activeTab === "suburb" ? "active" : ""
                        }`}
                        onClick={() => handleTabChange("suburb")}
                    >
                        Suburb PDF Editor
                    </button>
                </nav>

                <div className="sidebar-footer">
                    <p>Address Search</p>
                    <span>
                        Generate amenity score and heatmap from a property
                        address.
                    </span>
                </div>

                <div className="user-box">
                    <p>Logged in as</p>
                    <strong>{authUser.username}</strong>
                    <button onClick={handleLogout}>Logout</button>
                </div>
            </aside>

            <main className="main-content">
                <header className="page-header">
                    <div>
                        <p className="small-title">Property Investment Tools</p>
                        <h1>
                            {isMarketTab
                                ? "Market Trend Graph"
                                : "Suburb Statistics PDF Editor"}
                        </h1>
                    </div>

                    <div className="api-status">API Connected</div>
                </header>

                <section className="upload-card">
                    <div className="upload-info">
                        <p className="section-label">
                            {isMarketTab
                                ? "Market Report Tool"
                                : "Suburb Report Tool"}
                        </p>

                        <h2>
                            {isMarketTab
                                ? "Upload report and generate market trend graph"
                                : "Upload suburb report and generate edited PDF"}
                        </h2>

                        <p>
                            {isMarketTab
                                ? "Upload a property market report to create a clean market trend graph for investment analysis."
                                : "Upload a suburb statistics report to replace selected visual sections with clean chart outputs."}
                        </p>
                    </div>

                    <form className="upload-form" onSubmit={handleSubmit}>
                        <label className="file-upload-box">
                            <input
                                type="file"
                                accept="application/pdf"
                                onChange={handleFileChange}
                            />

                            <div className="upload-icon">⬆</div>

                            <strong>
                                {isMarketTab
                                    ? "Upload market report PDF"
                                    : "Upload suburb statistics PDF"}
                            </strong>

                            <small>Click here to select PDF file</small>
                        </label>

                        {currentFile && (
                            <div className="selected-file">
                                <div>
                                    <strong>{currentFile.name}</strong>
                                    <span>
                                        {formatFileSize(currentFile.size)}
                                    </span>
                                </div>

                                <button type="button" onClick={removeFile}>
                                    Remove
                                </button>
                            </div>
                        )}

                        {error && <div className="error-message">{error}</div>}

                        <button
                            type="submit"
                            className="submit-btn"
                            disabled={loading}
                        >
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
                        <h3>1. Upload PDF</h3>
                        <p>
                            Select the report file that you want the system to
                            analyse.
                        </p>
                    </div>

                    <div className="step-card">
                        <h3>2. Process Data</h3>
                        <p>
                            The backend extracts data and generates the required
                            output.
                        </p>
                    </div>

                    <div className="step-card">
                        <h3>3. Preview Output</h3>
                        <p>
                            View the generated graph or edited PDF directly
                            inside the app.
                        </p>
                    </div>
                </section>

                <section className="amenity-section">
                    <form
                        className="address-chat-box"
                        onSubmit={handleAmenitySearch}
                    >
                        <textarea
                            value={propertyAddress}
                            onChange={(event) =>
                                setPropertyAddress(event.target.value)
                            }
                            placeholder="Enter property address to generate amenity score and heatmap..."
                            rows="1"
                            disabled={amenityLoading}
                        />

                        <button type="submit" disabled={amenityLoading}>
                            {amenityLoading ? "Searching..." : "Search"}
                        </button>
                    </form>

                    {amenityLoading && (
                        <div className="amenity-loading-card">
                            Generating amenity score and heatmap...
                        </div>
                    )}

                    {amenityData && <AmenityResult data={amenityData} />}
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

function AuthPage({ onAuthSuccess }) {
    const [mode, setMode] = useState("login");

    const [formData, setFormData] = useState({
        username: "",
        email: "",
        password: "",
        confirm_password: "",
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    const isLogin = mode === "login";

    function handleChange(event) {
        const { name, value } = event.target;

        setFormData((previous) => ({
            ...previous,
            [name]: value,
        }));
    }

    async function handleSubmit(event) {
        event.preventDefault();

        setLoading(true);
        setError("");

        try {
            const data = isLogin
                ? await loginUser({
                      username: formData.username,
                      password: formData.password,
                  })
                : await registerUser({
                      username: formData.username,
                      email: formData.email,
                      password: formData.password,
                      confirm_password: formData.confirm_password,
                  });

            localStorage.setItem("authToken", data.token);
            localStorage.setItem("authUser", JSON.stringify(data.user));

            onAuthSuccess(data.user);
        } catch (error) {
            console.error(error);

            const backendError = error.response?.data;

            if (typeof backendError === "string") {
                setError(backendError);
            } else if (backendError?.error) {
                setError(backendError.error);
            } else if (backendError?.detail) {
                setError(backendError.detail);
            } else if (backendError) {
                const firstKey = Object.keys(backendError)[0];
                const firstMessage = backendError[firstKey];

                setError(
                    Array.isArray(firstMessage)
                        ? firstMessage[0]
                        : String(firstMessage)
                );
            } else {
                setError("Authentication failed. Please try again.");
            }
        } finally {
            setLoading(false);
        }
    }

    function switchMode() {
        setError("");
        setMode(isLogin ? "register" : "login");

        setShowPassword(false);
        setShowConfirmPassword(false);

        setFormData({
            username: "",
            email: "",
            password: "",
            confirm_password: "",
        });
    }

    return (
        <div className="auth-page">
            <div className="auth-card">
                <div className="auth-brand">
                    <div className="logo">AI</div>

                    <div>
                        <h1>AI Dashboard</h1>
                        <p>Login to use property report tools</p>
                    </div>
                </div>

                <h2>{isLogin ? "Login" : "Create Account"}</h2>

                <form onSubmit={handleSubmit} className="auth-form">
                    <label>
                        Username
                        <input
                            type="text"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            required
                        />
                    </label>

                    {!isLogin && (
                        <label>
                            Email
                            <input
                                type="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                            />
                        </label>
                    )}

                    <label>
                        Password
                        <div className="password-input-box">
                            <input
                                type={showPassword ? "text" : "password"}
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                required
                            />

                            <button
                                type="button"
                                className="password-toggle-btn"
                                onClick={() => setShowPassword(!showPassword)}
                                aria-label={
                                    showPassword
                                        ? "Hide password"
                                        : "Show password"
                                }
                            >
                                {showPassword ? "🙈" : "👁️"}
                            </button>
                        </div>
                    </label>

                    {!isLogin && (
                        <label>
                            Confirm Password
                            <div className="password-input-box">
                                <input
                                    type={
                                        showConfirmPassword
                                            ? "text"
                                            : "password"
                                    }
                                    name="confirm_password"
                                    value={formData.confirm_password}
                                    onChange={handleChange}
                                    required
                                />

                                <button
                                    type="button"
                                    className="password-toggle-btn"
                                    onClick={() =>
                                        setShowConfirmPassword(
                                            !showConfirmPassword
                                        )
                                    }
                                    aria-label={
                                        showConfirmPassword
                                            ? "Hide confirm password"
                                            : "Show confirm password"
                                    }
                                >
                                    {showConfirmPassword ? "🙈" : "👁️"}
                                </button>
                            </div>
                        </label>
                    )}

                    {error && <div className="error-message">{error}</div>}

                    <button
                        type="submit"
                        className="submit-btn"
                        disabled={loading}
                    >
                        {loading
                            ? "Please wait..."
                            : isLogin
                            ? "Login"
                            : "Create Account"}
                    </button>
                </form>

                <button
                    type="button"
                    className="switch-auth-btn"
                    onClick={switchMode}
                >
                    {isLogin
                        ? "New user? Create an account"
                        : "Already have an account? Login"}
                </button>
            </div>
        </div>
    );
}

function AmenityResult({ data }) {
    const heatmapUrl = getFullMediaUrl(data.heatmap_url);

    return (
        <section className="amenity-result">
            <div className="amenity-summary">
                <div>
                    <p className="small-title">Amenity Score Result</p>

                    <h2>
                        {data.total_score} / {data.score_out_of}
                    </h2>

                    <p>{data.interpretation}</p>
                    <span>{data.address}</span>
                </div>
            </div>

            {data.heatmap_url && (
                <div className="heatmap-preview-card">
                    <img
                        src={heatmapUrl}
                        alt="Amenity heatmap"
                        className="heatmap-image"
                    />
                </div>
            )}

            {Array.isArray(data.category_results) && (
                <div className="amenity-category-grid">
                    {data.category_results.map((item) => (
                        <div
                            className="amenity-category-card"
                            key={item.category}
                        >
                            <div className="category-top">
                                <h3>{item.category}</h3>
                                <strong>{item.score}/10</strong>
                            </div>

                            <p>{item.reason}</p>
                        </div>
                    ))}
                </div>
            )}
        </section>
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
                            <h3>No output received</h3>
                            <p>
                                The file was processed, but no preview link was
                                returned.
                            </p>
                        </div>
                    )}

                    {url && type === "image" && (
                        <img
                            className="image-preview"
                            src={url}
                            alt="Generated output"
                        />
                    )}

                    {url && type === "pdf" && (
                        <object
                            className="pdf-preview"
                            data={url}
                            type="application/pdf"
                        >
                            <div className="no-preview">
                                <h3>
                                    PDF preview is not available in this
                                    browser.
                                </h3>

                                <p>
                                    Please open the PDF in a new tab or download
                                    it.
                                </p>

                                <a href={url} target="_blank" rel="noreferrer">
                                    Open PDF
                                </a>
                            </div>
                        </object>
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
                            Open / Download Output
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