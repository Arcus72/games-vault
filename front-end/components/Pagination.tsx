import "./Pagination.css";

interface Props {
  currentPage: number;
  totalPages: number;
  setPage: (newPage: number) => void;
}

function getPageNumbers(
  currentPage: number,
  totalPages: number,
): (number | "...")[] {
  const pages = new Set([
    1,
    totalPages,
    currentPage - 1,
    currentPage,
    currentPage + 1,
  ]);
  const sorted = [...pages]
    .filter((p) => p >= 1 && p <= totalPages)
    .sort((a, b) => a - b);

  const result: (number | "...")[] = [];
  sorted.forEach((page, i) => {
    if (i > 0 && page - sorted[i - 1] > 1) result.push("...");
    result.push(page);
  });
  return result;
}

export default function Pagination({
  currentPage,
  totalPages,
  setPage,
}: Props) {
  const setNewPage = (page: number) => {
    if (page > 0) {
      setPage(page);
    }
  };

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
            onClick={() => setNewPage(page)}
          >
            {page}
          </button>
        ),
      )}
      {/* <button className="pagination__btn pagination__btn--next">&gt;</button> */}
    </nav>
  );
}
