import "./Pagination.css";

function getPageNumbers(currentPage: number, totalPages: number) {
  const sorted = [...new Set([1, totalPages, currentPage - 1, currentPage, currentPage + 1])]
    .filter((p) => p >= 1 && p <= totalPages)
    .sort((a, b) => a - b);

  return sorted.flatMap((page, i) =>
    i > 0 && page - sorted[i - 1] > 1 ? (["...", page] as const) : [page],
  );
}

export default function Pagination({
  currentPage,
  totalPages,
  setPage,
}: {
  currentPage: number;
  totalPages: number;
  setPage: (newPage: number) => void;
}) {
  return (
    <nav className="pagination">
      {getPageNumbers(currentPage, totalPages).map((page, i) =>
        page === "..." ? (
          <span key={`dots-${i}`} className="pagination__dots">
            ...
          </span>
        ) : (
          <button
            key={page}
            className={`pagination__btn${page === currentPage ? " pagination__btn--active" : ""}`}
            onClick={() => setPage(page)}
          >
            {page}
          </button>
        ),
      )}
    </nav>
  );
}
