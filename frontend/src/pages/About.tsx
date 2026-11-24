export default function About() {
  return (
    <div>
      <h2>About</h2>
      <div className="card">
        <p>
          <strong>Adaptive-RAG-OKF</strong> is a research demo for detecting hallucinations in
          Retrieval-Augmented Generation (RAG) outputs. It compares three models:
        </p>
        <ul>
          <li>
            <strong>baseline_rag</strong> — simple logistic regression over evidence features
          </li>
          <li>
            <strong>self_correction</strong> — gradient boosting classifier
          </li>
          <li>
            <strong>adaptive_okf</strong> — deeper gradient boosting with adaptive thresholds
          </li>
        </ul>
        <p>
          Features are extracted from answer/evidence overlap, sequence similarity, answer
          length, and numeric-claim detection. The backend exposes a FastAPI service, and the
          frontend is a React + TypeScript dashboard.
        </p>
      </div>
    </div>
  );
}
