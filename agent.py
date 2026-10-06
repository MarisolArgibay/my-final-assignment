from __future__ import annotations

from pathlib import Path
import concurrent.futures

from bootcamp_agent.agent import AgentResult, answer_question
from bootcamp_agent.config import load_settings
from bootcamp_agent.documents import Document, load_corpus
from bootcamp_agent.llm import LLMClient, get_client
from bootcamp_agent.retrieval import retrieve
from bootcamp_agent.schema import ResearchAnswer
from bootcamp_agent.tools import Tool, build_tools

CORPUS_DIR = Path(__file__).resolve().parent / "data" / "corpus"

REFUSAL = ResearchAnswer(
    answer="I don't know based on the provided corpus.",
    citations=(),
    confidence=0.0,
    needs_human_review=True,
)   

class YourAgent:
    """The agent the tests and the grader run."""
    
    timeout_s: float = 30.0
    
    def __init__(self, client: LLMClient | None = None) -> None:
        self.documents: list[Document] = load_corpus(CORPUS_DIR)
        self.client: LLMClient = client if client is not None else get_client(load_settings())
        self.tools: dict[str, Tool] = build_tools(self.documents, self.client)
       
    def run(self, question: str) -> AgentResult:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = executor.submit(
            answer_question,
            question,
            self.focus(question),
            self.client,
            max_tool_calls=3,
            top_k=3,
        )   
        try:
            result = future.result(timeout=self.timeout_s)
        except concurrent.futures.TimeoutError:
            return AgentResult(answer=REFUSAL, trace=())
        finally:
            executor.shutdown(wait=False, cancel_futures=True)
            
        answer = result.answer
        # A. No source means no answer: refuse, always in the same words.
        if not answer.citations:
            return AgentResult(answer=REFUSAL, trace=result.trace)
            
        # C. Show the evidence: quote the passage the answer comes from, word for word.
        cited = set(answer.citations)
        passages = [h for h in retrieve(question, self.documents, top_k=5) if h.chunk.doc_id in cited]
        if passages:
            best = passages[0].chunk
            answer = ResearchAnswer(
                answer=f"{answer.answer}\n\nSource [{best.doc_id}]: {best.text.strip()}",
                citations=answer.citations,
                confidence=answer.confidence,
                needs_human_review=answer.needs_human_review,
            )   
        return AgentResult(answer=answer, trace=result.trace)
       
    def focus(self, question: str) -> list[Document]:
        """When one document clearly matches best, give the model only that one."""
        best: dict[str, float] = {}
        for hit in retrieve(question, self.documents, top_k=5):
            best[hit.chunk.doc_id] = max(best.get(hit.chunk.doc_id, 0.0), hit.score)
        if not best:                                                         
            return self.documents
        ranked = sorted(best.values(), reverse=True)
        top_doc = max(best, key=best.get)
        if len(ranked) == 1 or ranked[0] >= 1.5 * ranked[1]:
            return [doc for doc in self.documents if doc.doc_id == top_doc]
        return self.documents
       
    def __call__(self, question: str) -> ResearchAnswer:
        return self.run(question).answer