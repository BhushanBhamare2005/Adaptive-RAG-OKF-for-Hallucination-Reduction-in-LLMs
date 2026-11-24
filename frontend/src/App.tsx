import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Sidebar from './components/common/Sidebar';
import Navbar from './components/common/Navbar';
import Overview from './pages/Overview';
import KnowledgeBase from './pages/KnowledgeBase';
import DocumentUpload from './pages/DocumentUpload';
import RAGPlayground from './pages/RAGPlayground';
import ClaimVerification from './pages/ClaimVerification';
import AdaptiveOKF from './pages/AdaptiveOKF';
import AEVL from './pages/AEVL';
import EvidenceConflicts from './pages/EvidenceConflicts';
import ModelEvaluation from './pages/Experiments';
import Explainability from './pages/Explainability';
import AuditLogs from './pages/AuditLogs';
import Settings from './pages/Settings';
import DatasetExplorer from './pages/DatasetExplorer';
import Analyze from './pages/Analyze';
import About from './pages/About';

export default function App() {
  const [collapsed, setCollapsed] = React.useState(false);
  return (
    <div className={collapsed ? 'app-shell sidebar-collapsed' : 'app-shell'}>
      <Sidebar collapsed={collapsed} />
      <div className="app-main">
        <Navbar collapsed={collapsed} onToggle={() => setCollapsed((value) => !value)} />
        <main className="page-content">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/knowledge" element={<KnowledgeBase />} />
            <Route path="/upload" element={<DocumentUpload />} />
            <Route path="/rag" element={<RAGPlayground />} />
            <Route path="/claims" element={<ClaimVerification />} />
            <Route path="/adaptive-okf" element={<AdaptiveOKF />} />
            <Route path="/aevl" element={<AEVL />} />
            <Route path="/conflicts" element={<EvidenceConflicts />} />
            <Route path="/models" element={<ModelEvaluation />} />
            <Route path="/experiments" element={<ModelEvaluation />} />
            <Route path="/explainability" element={<Explainability />} />
            <Route path="/audit" element={<AuditLogs />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/datasets" element={<DatasetExplorer />} />
            <Route path="/analyze" element={<Analyze />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
