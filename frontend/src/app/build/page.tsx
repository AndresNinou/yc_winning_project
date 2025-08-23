import ResultsClient from "./ResultsClient";

export default function Page({
  searchParams,
}: {
  searchParams: { q?: string; name?: string };
}) {
  return <ResultsClient searchParams={searchParams} />;
}
