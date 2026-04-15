import { ContentLayout } from '@/components/layouts/content-layout';

export default function GoalsRoute() {
  const isLoading = false;
  const hasError = false;

  return (
    <ContentLayout title="Goals">
      <div className="space-y-6">
        <section className="rounded-md border p-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">Your fitness goals</h2>
              <p className="text-sm text-gray-600">
                Create and track goals for your activities.
              </p>
            </div>

            <button className="rounded-md border px-3 py-2">
              + Create Goal
            </button>
          </div>
        </section>

        {isLoading ? (
          <div className="rounded-md border p-4 animate-pulse">
            Loading goals...
          </div>
        ) : hasError ? (
          <div className="rounded-md border border-red-300 p-4">
            Something went wrong while loading your goals.
          </div>
        ) : (
          <>
            <section className="rounded-md border p-4">
              <h3 className="mb-3 text-md font-semibold">Active goals</h3>
              <p className="text-sm text-gray-600">
                No active goals yet. Create your first goal to start tracking
                progress.
              </p>
            </section>

            <section className="rounded-md border p-4">
              <h3 className="mb-3 text-md font-semibold">Completed goals</h3>
              <p className="text-sm text-gray-600">
                Completed goals will appear here.
              </p>
            </section>
          </>
        )}
      </div>
    </ContentLayout>
  );
}