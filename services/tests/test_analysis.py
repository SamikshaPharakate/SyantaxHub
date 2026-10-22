import sys
import os
import unittest

# Ensure services directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.rag_engine import rag_engine
from core.llm_provider import llm_provider

class TestCodeAnalysisAccuracy(unittest.TestCase):

    def test_valid_react_19_code(self):
        """Valid React 19 code with hooks and ref prop must be classified as CURRENT."""
        valid_react_19_code = """
import { useState } from 'react';

export function ModernCard({ title, ref }: { title: string; ref?: React.Ref<HTMLDivElement> }) {
  const [active, setActive] = useState(false);
  return (
    <div ref={ref} className="card" onClick={() => setActive(!active)}>
      <h3>{title}</h3>
      <p>Status: {active ? 'Active' : 'Inactive'}</p>
    </div>
  );
}
"""
        result = rag_engine.analyze_code(
            code=valid_react_19_code,
            language="javascript",
            technology="React",
            version="19"
        )
        self.assertEqual(result["status"], "current", f"Expected 'current', got '{result['status']}'")

    def test_deprecated_javascript_substr(self):
        """JavaScript code using legacy String.prototype.substr() must be classified as OUTDATED."""
        deprecated_js_code = """
function getFileExtension(filename) {
  const dotIndex = filename.lastIndexOf('.');
  if (dotIndex === -1) return '';
  return filename.substr(dotIndex + 1);
}
"""
        result = rag_engine.analyze_code(
            code=deprecated_js_code,
            language="javascript",
            technology="JavaScript",
            version="ES2024"
        )
        self.assertEqual(result["status"], "outdated", f"Expected 'outdated', got '{result['status']}'")

    def test_valid_javascript_slice(self):
        """JavaScript code using standard modern String.prototype.slice() must be classified as CURRENT."""
        valid_slice_code = """
const getSubdomain = (hostname) => {
  const parts = hostname.split('.');
  return parts.slice(0, -2).join('.');
};
"""
        result = rag_engine.analyze_code(
            code=valid_slice_code,
            language="javascript",
            technology="JavaScript",
            version="ES2024"
        )
        self.assertEqual(result["status"], "current", f"Expected 'current', got '{result['status']}'")

    def test_ai_explanation_mentioning_deprecated_does_not_cause_false_positive(self):
        """Valid code must NOT be marked OUTDATED merely because explanation discusses deprecated APIs."""
        valid_code = "const domain = url.slice(0, 10);"
        explanation_with_deprecated_keywords = """
STATUS: CURRENT

### Executive Summary
**Overall Code Health: Current & Compliant.**
The submitted code uses `slice()`, which adheres to ECMAScript standards.
Note that the legacy method `substr()` is deprecated and obsolete in modern JavaScript.
Furthermore, class components with `componentDidMount` were deprecated in React.
However, none of those outdated patterns are present in your code.

### Detected Issues
No deprecated or outdated patterns detected.
"""
        status = rag_engine._determine_status(
            analysis_text=explanation_with_deprecated_keywords,
            code=valid_code,
            language="javascript",
            technology="JavaScript",
            version="ES2024"
        )
        self.assertEqual(status, "current", f"Expected 'current' despite deprecated keywords in explanation, got '{status}'")

    def test_react_19_warning_status(self):
        """Optimization suggestions (e.g. useEffect fetch waterfall) should yield WARNING, not OUTDATED."""
        warning_code = """
import { useState, useEffect } from 'react';

export function UserList() {
  const [users, setUsers] = useState([]);
  useEffect(() => {
    fetch('/api/users').then(res => res.json()).then(setUsers);
  }, []);
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
"""
        result = rag_engine.analyze_code(
            code=warning_code,
            language="javascript",
            technology="React",
            version="19"
        )
        self.assertEqual(result["status"], "warning", f"Expected 'warning', got '{result['status']}'")

    def test_insufficient_evidence_returns_uncertain(self):
        """When code is empty or has insufficient syntax, return UNCERTAIN instead of inventing a classification."""
        empty_code = "   "
        result = rag_engine.analyze_code(
            code=empty_code,
            language="unknown",
            technology="",
            version=""
        )
        self.assertEqual(result["status"], "uncertain", f"Expected 'uncertain', got '{result['status']}'")

if __name__ == "__main__":
    unittest.main()
