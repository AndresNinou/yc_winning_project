"use client";
import ResultsClient from "./ResultsClient";

export default function Page({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; name?: string }>;
}) {
  return <ResultsClient searchParams={searchParams} />;
}
