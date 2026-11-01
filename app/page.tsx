import site from '../content/site.json';

export default function Page() {
  return (
    <main>
      <h1>{site.title}</h1>
      <p data-lbs-run={site.runId}>LBS run {site.runId}</p>
    </main>
  );
}
