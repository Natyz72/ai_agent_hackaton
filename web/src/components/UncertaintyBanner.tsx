// HARD RULES: The uncertainty banner is always visible on Results, Review, and Incident detail pages:
// "No warning signs detected does not mean this message is safe."
export function UncertaintyBanner() {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4" role="note" aria-live="polite">
      <p className="text-sm text-blue-900 font-medium">
        No warning signs detected does not mean this message is safe.
      </p>
    </div>
  );
}
