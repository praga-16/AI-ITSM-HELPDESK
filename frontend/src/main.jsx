import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BrowserRouter,
  useLocation,
  useNavigate,
} from "react-router-dom";

import {
  Bot,
  LayoutDashboard,
  Ticket,
  BookOpen,
  Boxes,
  Settings2,
  Activity,
  Menu,
  X,
  ShieldCheck,
  ArrowUp,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
} from "lucide-react";

import "./style.css";

const API = "http://127.0.0.1:8004";

/* =========================================================
   DEMO SCENARIOS
========================================================= */

const demos = [
  ["VPN Incident", "My VPN is not connecting."],
  ["Self-Heal", "My password has expired."],
  ["RAG", "How do I troubleshoot Outlook synchronization?"],
  ["Software", "I need Visual Studio Code installed on my laptop."],
  ["Unknown", "What is the company's quantum computing strategy."],
];

/* =========================================================
   API
========================================================= */

async function get(path, options = {}) {
  const response = await fetch(API + path, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json();
}

/* =========================================================
   HELPERS
========================================================= */

function safe(value, fallback = "—") {
  if (
    value === undefined ||
    value === null ||
    value === "" ||
    value === "undefined" ||
    value === "null"
  ) {
    return fallback;
  }

  return value;
}

function formatStatus(value) {
  if (!value) return "—";

  return String(value)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function getServiceNowNumber(item) {
  return (
    item?.servicenow?.number ||
    item?.service_now?.number ||
    item?.ticket?.number ||
    item?.request?.number ||
    item?.number ||
    item?.ticket_id ||
    item?.request_id ||
    "—"
  );
}

function getTicketReference(ticket) {
  return (
    ticket?.ticket_id ||
    ticket?.ticket?.ticket_id ||
    ticket?.ticket?.number ||
    ticket?.servicenow?.number ||
    ticket?.service_now?.number ||
    ticket?.number ||
    "—"
  );
}

function getTicketStatus(ticket) {
  return (
    ticket?.status ||
    ticket?.ticket?.status ||
    ticket?.servicenow?.state ||
    ticket?.service_now?.state ||
    "New"
  );
}

function getSoftwareRequestId(request) {
  return (
    request?.request_id ||
    request?.software_request?.request_id ||
    request?.servicenow?.number ||
    request?.service_now?.number ||
    request?.number ||
    "—"
  );
}

function getSoftwareName(request) {
  return (
    request?.software ||
    request?.software_name ||
    request?.software_request?.software ||
    request?.software_request?.software_name ||
    request?.servicenow?.software ||
    request?.servicenow?.short_description ||
    request?.analysis?.software ||
    "Software Request"
  );
}

function getSoftwareStatus(request) {
  return (
    request?.status ||
    request?.software_request?.status ||
    request?.automation?.status ||
    request?.servicenow?.state ||
    request?.service_now?.state ||
    "Pending Approval"
  );
}

function getAutomationAction(item) {
  return (
    item?.action ||
    item?.automation?.action ||
    item?.workflow ||
    item?.automation_type ||
    "automation workflow"
  );
}

function getAutomationStatus(item) {
  return (
    item?.status ||
    item?.automation?.status ||
    "completed"
  );
}

function getAutomationReference(item) {
  return (
    item?.servicenow_number ||
    item?.servicenow?.number ||
    item?.service_now?.number ||
    item?.ticket_id ||
    item?.request_id ||
    item?.automation?.servicenow_number ||
    null
  );
}

function getAutomationTime(item) {
  return (
    item?.timestamp ||
    item?.created_at ||
    item?.updated_at ||
    ""
  );
}

/* =========================================================
   APP
========================================================= */

function App() {
  const location = useLocation();
  const navigate = useNavigate();

  const [open, setOpen] = useState(false);

  const links = [
    ["/", "Dashboard", LayoutDashboard],
    ["/self-service", "AI Self-Service", Bot],
    ["/tickets", "ITSM Tickets", Ticket],
    ["/ai-analysis", "AI Analysis", Activity],
    ["/knowledge", "Knowledge Base", BookOpen],
    ["/software", "Software Requests", Boxes],
    ["/automation", "Automation", Settings2],
  ];

  return (
    <div className="app">

      <aside className={open ? "side open" : "side"}>

        <div className="brand">
          <b>AI</b>

          <div>
            <strong>ITSM</strong>
            <small>Helpdesk Automation</small>
          </div>
        </div>

        <span className="navlabel">
          WORKSPACE
        </span>

        {links.map(([path, label, Icon]) => (
          <button
            key={path}
            onClick={() => {
              navigate(path);
              setOpen(false);
            }}
            className={
              location.pathname === path
                ? "nav active"
                : "nav"
            }
          >
            <Icon size={18} />
            {label}
          </button>
        ))}

        <div className="gov">
          <ShieldCheck size={17} />

          <div>
            <b>AI Governance</b>
            <small>
              Grounded responses enabled
            </small>
          </div>
        </div>

      </aside>

      {open && (
        <div
          className="overlay"
          onClick={() => setOpen(false)}
        />
      )}

      <main className="main">

        <header>

          <button
            className="menubtn"
            onClick={() => setOpen(!open)}
          >
            {open ? <X /> : <Menu />}
          </button>

          <div>
            <small>
              ENTERPRISE AI OPERATIONS
            </small>

            <h1>
              {title(location.pathname)}
            </h1>
          </div>

          <span className="online">
            • System Online
          </span>

          <div className="avatar">
            PS
          </div>

        </header>

        <div className="content">
          <RoutesView path={location.pathname} />
        </div>

      </main>

    </div>
  );
}

/* =========================================================
   PAGE TITLES
========================================================= */

function title(path) {

  if (path === "/") {
    return "Operations Dashboard";
  }

  if (path.includes("self-service")) {
    return "AI Self-Service";
  }

  if (path.includes("tickets")) {
    return "ITSM Tickets";
  }

  if (path.includes("ai-analysis")) {
    return "AI Analysis";
  }

  if (path.includes("knowledge")) {
    return "Knowledge Base";
  }

  if (path.includes("software")) {
    return "Software Provisioning";
  }

  return "Automation Center";
}

/* =========================================================
   ROUTES
========================================================= */

function RoutesView({ path }) {

  if (path === "/") {
    return <Dashboard />;
  }

  if (path === "/self-service") {
    return <Chat />;
  }

  if (path === "/tickets") {
    return <Tickets />;
  }

  if (path === "/ai-analysis") {
    return <Analysis />;
  }

  if (path === "/knowledge") {
    return <Knowledge />;
  }

  if (path === "/software") {
    return <Software />;
  }

  return <Automation />;
}

/* =========================================================
   UI
========================================================= */

function Card({ children, className = "" }) {

  return (
    <section className={"card " + className}>
      {children}
    </section>
  );
}

function Header({ k, title }) {

  return (
    <div className="chead">

      <div>

        <small>{k}</small>

        <h2>{title}</h2>

      </div>

    </div>
  );
}

function Stat({
  icon: Icon,
  label,
  value,
  hint,
}) {

  return (
    <div className="stat">

      <div className="sicon">
        <Icon size={18} />
      </div>

      <div>

        <small>{label}</small>

        <b>{value}</b>

        <em>{hint}</em>

      </div>

    </div>
  );
}

/* =========================================================
   DASHBOARD
========================================================= */

function Dashboard() {

  const [stats, setStats] = useState({});

  useEffect(() => {

    get("/api/dashboard/stats")
      .then(setStats)
      .catch((error) => {
        console.error(
          "Dashboard error:",
          error
        );
      });

  }, []);

  return (
    <>

      <div className="hero">

        <div>

          <small>
            AI OPERATIONS CENTER
          </small>

          <h2>
            Resolve IT issues before they become tickets.
          </h2>

          <p>
            AI understanding + approved knowledge +
            safe automation + ServiceNow workflows.
          </p>

        </div>

        <button
          className="primary"
          onClick={() => {
            window.location.href =
              "/self-service";
          }}
        >
          <Bot size={17} />
          Open AI Assistant
        </button>

      </div>

      <div className="stats">

        {[
          [
            Ticket,
            "Total Tickets",
            stats.total_tickets || 0,
            "All incidents",
          ],
          [
            Activity,
            "Open Tickets",
            stats.open_tickets || 0,
            "Needs attention",
          ],
          [
            CheckCircle2,
            "AI Resolved",
            stats.ai_resolved || 0,
            "Automated",
          ],
          [
            AlertTriangle,
            "Escalated",
            stats.escalated || 0,
            "Human review",
          ],
          [
            Boxes,
            "Software Requests",
            stats.software_requests || 0,
            "Provisioning",
          ],
          [
            Activity,
            "Automation Actions",
            stats.automation_actions || 0,
            "Audit events",
          ],
        ].map((item) => (

          <Stat
            key={item[1]}
            icon={item[0]}
            label={item[1]}
            value={item[2]}
            hint={item[3]}
          />

        ))}

      </div>

      <div className="cols">

        <Card>

          <Header
            k="HACKATHON FLOW"
            title="Enterprise journey"
          />

          <div className="flow">

            {[
              "Employee Request",
              "AI Understanding",
              "Knowledge Retrieval",
              "Intelligent Decision",
              "Automation",
              "ServiceNow",
              "Resolution",
            ].map((item, index) => (

              <div key={item}>

                <b>{index + 1}</b>

                <span>{item}</span>

              </div>

            ))}

          </div>

        </Card>

        <Card>

          <Header
            k="DEMO READY"
            title="Five scenarios"
          />

          {demos.map((item, index) => (

            <div
              className="scenario"
              key={item[0]}
            >

              <b>
                0{index + 1}
              </b>

              <div>

                <strong>
                  {item[0]}
                </strong>

                <small>
                  {item[1]}
                </small>

              </div>

            </div>

          ))}

        </Card>

      </div>

    </>
  );
}

/* =========================================================
   AI SELF SERVICE
========================================================= */

function Chat() {

  const [text, setText] = useState("");

  const [messages, setMessages] =
    useState([]);

  const [busy, setBusy] =
    useState(false);

  const [last, setLast] =
    useState(null);

  async function send(value = text) {

    if (!value.trim() || busy) {
      return;
    }

    setMessages((current) => [
      ...current,
      {
        role: "u",
        text: value,
      },
    ]);

    setText("");
    setBusy(true);

    try {

      const result =
        await get("/api/chat", {
          method: "POST",

          body: JSON.stringify({
            message: value,
          }),
        });

      setMessages((current) => [
        ...current,
        {
          role: "a",

          text:
            result.response ||
            result.answer ||
            result.message ||
            "I could not generate a response.",
        },
      ]);

      setLast(result);

    } catch (error) {

      console.error(error);

      setMessages((current) => [
        ...current,
        {
          role: "a",
          text:
            "The AI service is unavailable. Confirm the FastAPI backend is running on port 8004.",
        },
      ]);

    } finally {

      setBusy(false);

    }
  }

  return (
    <div className="workspace">

      <Card className="chat">

        <div className="chathead">

          <div className="bot">
            <Bot />
          </div>

          <div>

            <b>
              AI Helpdesk Assistant
            </b>

            <small>
              Grounded in approved enterprise knowledge
            </small>

          </div>

          <span className="live">
            • Live
          </span>

        </div>

        <div className="demos">

          <small>
            QUICK DEMO
          </small>

          {demos.map((item) => (

            <button
              key={item[0]}
              onClick={() => send(item[1])}
            >
              {item[0]}
            </button>

          ))}

        </div>

        <div className="messages">

          {!messages.length && (

            <div className="empty">

              <Sparkles size={30} />

              <h2>
                How can I help today?
              </h2>

              <p>
                Describe an IT issue, ask a
                knowledge question, or request software.
              </p>

            </div>

          )}

          {messages.map(
            (message, index) => (

              <div
                key={index}
                className={
                  "msg " +
                  message.role
                }
              >

                <div>
                  {message.text}
                </div>

              </div>

            )
          )}

          {busy && (

            <div className="msg a">

              <div>
                AI is analyzing...
              </div>

            </div>

          )}

        </div>

        <form
          className="input"
          onSubmit={(event) => {

            event.preventDefault();

            send();

          }}
        >

          <input
            value={text}
            onChange={(event) =>
              setText(event.target.value)
            }
            placeholder="Describe your IT issue..."
          />

          <button type="submit">
            <ArrowUp />
          </button>

        </form>

      </Card>

      <div className="right">

        {last && (

          <Card>

            <Header
              k="AI DECISION"
              title="Analysis"
            />

            <AnalysisData
              a={last.analysis}
              confidence={last.confidence}
            />

          </Card>

        )}

        {last?.sources?.length > 0 && (

          <Card>

            <Header
              k="RAG"
              title="Knowledge Sources"
            />

            {last.sources.map(
              (source, index) => (

                <div
                  className="source"
                  key={index}
                >

                  <b>
                    {source.name ||
                      source.title ||
                      source.source ||
                      "Knowledge Source"}
                  </b>

                  <small>
                    Similarity{" "}
                    {source.score !== undefined
                      ? (
                          Number(
                            source.score
                          ) * 100
                        ).toFixed(0) + "%"
                      : "—"}
                  </small>

                  <p>
                    {source.excerpt ||
                      source.text ||
                      source.content ||
                      ""}
                  </p>

                </div>

              )
            )}

          </Card>

        )}

        {last?.automation && (

          <Card>

            <Header
              k="AGENT"
              title="Automation Timeline"
            />

            <div className="timeline">

              <b>
                {formatStatus(
                  last.automation.action
                )}
              </b>

              <small>
                {formatStatus(
                  last.automation.status
                )}
              </small>

              {getAutomationReference(
                last.automation
              ) && (

                <small>
                  ServiceNow:{" "}
                  {getAutomationReference(
                    last.automation
                  )}
                </small>

              )}

            </div>

          </Card>

        )}

        {last?.ticket && (

          <div className="refbox">

            ServiceNow Incident

            <br />

            <strong>
              {getTicketReference(
                last.ticket
              )}
            </strong>

            <small>
              {getTicketStatus(
                last.ticket
              )}
            </small>

          </div>

        )}

        {last?.servicenow &&
          !last?.ticket &&
          last.servicenow.number && (

            <div className="refbox">

              ServiceNow Reference

              <br />

              <strong>
                {last.servicenow.number}
              </strong>

              <small>
                {formatStatus(
                  last.servicenow.state
                )}
              </small>

            </div>

          )}

        {last?.software_request && (

          <div className="refbox">

            Provisioning Request

            <br />

            <strong>
              {getSoftwareRequestId(last)}
            </strong>

            <small>
              {formatStatus(
                getSoftwareStatus(last)
              )}
            </small>

          </div>

        )}

      </div>

    </div>
  );
}

/* =========================================================
   ANALYSIS DATA
========================================================= */

function AnalysisData({
  a,
  confidence,
}) {

  if (!a) {
    return null;
  }

  const values = [
    ["Intent", a.intent],
    ["Category", a.category],
    ["Sub-category", a.subcategory],
    ["Priority", a.priority],
    ["Impact", a.impact],
    ["Urgency", a.urgency],
    ["Assignment", a.assignment_group],
    ["Summary", a.summary],
  ];

  const confidenceValue =
    confidence ??
    a.confidence ??
    0;

  return (
    <>

      <div className="analysisgrid">

        {values.map((item) => (

          <div key={item[0]}>

            <small>
              {item[0]}
            </small>

            <b>
              {safe(item[1])}
            </b>

          </div>

        ))}

      </div>

      <div className="resolution">

        <small>
          CONFIDENCE
        </small>

        <b>
          {Math.round(
            Number(confidenceValue) * 100
          )}
          %
        </b>

        <span>
          {safe(
            a.suggested_resolution,
            "Grounded enterprise knowledge"
          )}
        </span>

      </div>

    </>
  );
}

/* =========================================================
   TICKETS
========================================================= */

function Tickets() {

  const [tickets, setTickets] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  const load = async () => {

    setLoading(true);

    try {

      const result =
        await get("/api/tickets");

      setTickets(
        Array.isArray(result.tickets)
          ? result.tickets
          : []
      );

    } catch (error) {

      console.error(
        "Tickets error:",
        error
      );

      setTickets([]);

    } finally {

      setLoading(false);

    }
  };

  useEffect(() => {
    load();
  }, []);

  const rows = tickets.map(
    (ticket) => {

      const analysis =
        ticket.analysis ||
        ticket.ticket?.analysis ||
        {};

      const reference =
        getTicketReference(ticket);

      const status =
        getTicketStatus(ticket);

      const summary =
        analysis.summary ||
        ticket.summary ||
        ticket.ticket?.summary ||
        ticket.servicenow?.short_description ||
        "IT Support Request";

      const category =
        analysis.category ||
        ticket.category ||
        ticket.ticket?.category ||
        ticket.servicenow?.category ||
        "General";

      const priority =
        analysis.priority ||
        ticket.priority ||
        ticket.ticket?.priority ||
        ticket.servicenow?.priority ||
        "P3";

      const ai =
        ticket.ai_resolved === true
          ? "Resolved"
          : "Assisted";

      return [
        reference,
        summary,
        category,
        priority,
        formatStatus(status),
        ai,
      ];
    }
  );

  return (
    <Card>

      <Header
        k="ITSM"
        title="Tickets"
      />

      <button
        className="ghost"
        onClick={load}
        disabled={loading}
      >
        <RefreshCw size={14} />

        {loading
          ? "Loading..."
          : "Refresh"}
      </button>

      <Table
        head={[
          "Reference",
          "Summary",
          "Category",
          "Priority",
          "Status",
          "AI",
        ]}
        rows={rows}
      />

    </Card>
  );
}

/* =========================================================
   AI ANALYSIS PAGE
========================================================= */

function Analysis() {

  const [query, setQuery] =
    useState(
      "My VPN is not connecting."
    );

  const [result, setResult] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  async function analyze(event) {

    event.preventDefault();

    if (!query.trim()) {
      return;
    }

    setLoading(true);

    try {

      const response =
        await get("/api/chat", {
          method: "POST",

          body: JSON.stringify({
            message: query,
          }),
        });

      setResult(response);

    } catch (error) {

      console.error(error);

    } finally {

      setLoading(false);

    }
  }

  return (
    <>

      <Card>

        <Header
          k="AI DECISION ENGINE"
          title="Analyze a request"
        />

        <form
          className="search"
          onSubmit={analyze}
        >

          <input
            value={query}
            onChange={(event) =>
              setQuery(event.target.value)
            }
          />

          <button
            className="primary"
            disabled={loading}
          >
            {loading
              ? "Analyzing..."
              : "Analyze"}
          </button>

        </form>

      </Card>

      {result && (

        <div className="cols">

          <Card>

            <Header
              k="CLASSIFICATION"
              title="AI Fields"
            />

            <AnalysisData
              a={result.analysis}
              confidence={result.confidence}
            />

          </Card>

          <Card>

            <Header
              k="RESPONSE"
              title="Grounded Result"
            />

            <p className="answer">
              {result.response}
            </p>

            {result.sources?.map(
              (source, index) => (

                <div
                  className="source"
                  key={index}
                >

                  <b>
                    {source.name ||
                      source.title ||
                      source.source}
                  </b>

                  <small>
                    {source.score !== undefined
                      ? (
                          Number(
                            source.score
                          ) * 100
                        ).toFixed(0) + "%"
                      : ""}
                  </small>

                </div>

              )
            )}

          </Card>

        </div>

      )}

    </>
  );
}

/* =========================================================
   KNOWLEDGE BASE
========================================================= */

function Knowledge() {

  const [documents, setDocuments] =
    useState([]);

  const [query, setQuery] =
    useState(
      "How do I troubleshoot Outlook synchronization?"
    );

  const [results, setResults] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  useEffect(() => {

    get("/api/knowledge")
      .then((result) => {

        setDocuments(
          Array.isArray(result.documents)
            ? result.documents
            : []
        );

      })
      .catch((error) => {

        console.error(
          "Knowledge error:",
          error
        );

      });

  }, []);

  async function search(event) {

    event.preventDefault();

    if (!query.trim()) {
      return;
    }

    setLoading(true);

    try {

      const response =
        await get(
          "/api/knowledge/search",
          {
            method: "POST",

            body: JSON.stringify({
              query,
              top_k: 4,
            }),
          }
        );

      setResults(
        Array.isArray(response.results)
          ? response.results
          : []
      );

    } catch (error) {

      console.error(
        "RAG search error:",
        error
      );

      setResults([]);

    } finally {

      setLoading(false);

    }
  }

  return (
    <div className="cols">

      <Card>

        <Header
          k="ENTERPRISE CONTENT"
          title="Knowledge Articles"
        />

        {documents.map(
          (document, index) => (

            <div
              className="doc"
              key={index}
            >

              <BookOpen size={16} />

              <b>
                {document.name ||
                  document.source ||
                  document.title}
              </b>

            </div>

          )
        )}

      </Card>

      <Card>

        <Header
          k="SEMANTIC SEARCH"
          title="RAG Explorer"
        />

        <form
          className="search"
          onSubmit={search}
        >

          <input
            value={query}
            onChange={(event) =>
              setQuery(event.target.value)
            }
          />

          <button
            className="primary"
            disabled={loading}
          >
            {loading
              ? "Searching..."
              : "Search"}
          </button>

        </form>

        {!loading &&
          results.length === 0 && (

            <div
              className="empty"
              style={{
                minHeight: "180px",
              }}
            >

              <BookOpen size={28} />

              <h2>
                Search the knowledge base
              </h2>

              <p>
                Semantic search results will
                appear here.
              </p>

            </div>

          )}

        {results.map(
          (source, index) => (

            <div
              className="source"
              key={index}
            >

              <b>
                📄{" "}
                {source.name ||
                  source.title ||
                  source.source ||
                  "Knowledge Source"}
              </b>

              <small>
                Similarity{" "}
                {source.score !== undefined
                  ? (
                      Number(source.score) *
                      100
                    ).toFixed(0) + "%"
                  : "—"}
              </small>

              <p>
                {source.text ||
                  source.excerpt ||
                  source.content ||
                  ""}
              </p>

            </div>

          )
        )}

      </Card>

    </div>
  );
}

/* =========================================================
   SOFTWARE REQUESTS
========================================================= */

function Software() {

  const [requests, setRequests] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  const load = async () => {

    setLoading(true);

    try {

      const response =
        await get(
          "/api/software/requests"
        );

      setRequests(
        Array.isArray(response.requests)
          ? response.requests
          : []
      );

    } catch (error) {

      console.error(
        "Software requests error:",
        error
      );

      setRequests([]);

    } finally {

      setLoading(false);

    }
  };

  useEffect(() => {
    load();
  }, []);

  const rows = requests.map(
    (request) => [

      getSoftwareRequestId(request),

      getSoftwareName(request),

      formatStatus(
        getSoftwareStatus(request)
      ),

      getServiceNowNumber(request),

    ]
  );

  return (
    <Card>

      <Header
        k="PROVISIONING"
        title="Software Requests"
      />

      <button
        className="ghost"
        onClick={load}
        disabled={loading}
      >

        <RefreshCw size={14} />

        {loading
          ? "Loading..."
          : "Refresh"}

      </button>

      <Table
        head={[
          "Request",
          "Software",
          "Status",
          "ServiceNow",
        ]}
        rows={rows}
      />

    </Card>
  );
}

/* =========================================================
   AUTOMATION
========================================================= */

function Automation() {

  const [logs, setLogs] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  const load = async () => {

    setLoading(true);

    try {

      const response =
        await get(
          "/api/automation/logs"
        );

      setLogs(
        Array.isArray(response.logs)
          ? response.logs
          : []
      );

    } catch (error) {

      console.error(
        "Automation error:",
        error
      );

      setLogs([]);

    } finally {

      setLoading(false);

    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <Card>

      <Header
        k="AUDIT TRAIL"
        title="Automation Actions"
      />

      <button
        className="ghost"
        onClick={load}
        disabled={loading}
      >

        <RefreshCw size={14} />

        {loading
          ? "Loading..."
          : "Refresh"}

      </button>

      {logs.length === 0 && (

        <div className="empty">

          <Activity size={28} />

          <h2>
            No automation actions yet
          </h2>

          <p>
            Run one of the AI demo scenarios
            to generate an automation event.
          </p>

        </div>

      )}

      {logs.map(
        (automation, index) => {

          const reference =
            getAutomationReference(
              automation
            );

          return (
            <div
              className="timeline"
              key={index}
            >

              <b>
                ✓{" "}
                {formatStatus(
                  getAutomationAction(
                    automation
                  )
                )}
              </b>

              <small>

                {getAutomationTime(
                  automation
                )}

                {getAutomationTime(
                  automation
                )
                  ? " · "
                  : ""}

                {formatStatus(
                  getAutomationStatus(
                    automation
                  )
                )}

              </small>

              {reference && (

                <small>
                  ServiceNow: {reference}
                </small>

              )}

              {automation.message && (

                <small>
                  {automation.message}
                </small>

              )}

            </div>
          );
        }
      )}

    </Card>
  );
}

/* =========================================================
   TABLE
========================================================= */

function Table({
  head,
  rows,
}) {

  return (
    <div className="tablewrap">

      <table>

        <thead>

          <tr>

            {head.map((heading) => (

              <th key={heading}>
                {heading}
              </th>

            ))}

          </tr>

        </thead>

        <tbody>

          {rows.map(
            (row, rowIndex) => (

              <tr key={rowIndex}>

                {row.map(
                  (cell, cellIndex) => (

                    <td key={cellIndex}>

                      {cellIndex === 0 ? (

                        <b className="purple">
                          {safe(cell)}
                        </b>

                      ) : (

                        safe(cell)

                      )}

                    </td>

                  )
                )}

              </tr>

            )
          )}

        </tbody>

      </table>

    </div>
  );
}

/* =========================================================
   START
========================================================= */

createRoot(
  document.getElementById("root")
).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
);