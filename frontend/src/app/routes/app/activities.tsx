import { ContentLayout } from '@/components/layouts/content-layout';

export default function ActivitiesRoute() {
  const isLoading = false;
  const hasError = false;

  return (
    <ContentLayout title="Activities">
      {isLoading ? (
        <div className="animate-pulse rounded-md border p-4">
          Loading activities...
        </div>
      ) : hasError ? (
        <div className="rounded-md border border-red-300 p-4">
          Something went wrong while loading activities.
        </div>
      ) : (
        <p>Activities page scaffold (Group 18)</p>
      )}
    </ContentLayout>
  );
}

//this code was developed from chatGPT code