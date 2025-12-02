import { useParams } from 'react-router-dom';

export default function DealDetail() {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="p-8">
      <h1 className="text-3xl font-heading font-semibold mb-4">Deal #{id}</h1>
      <p className="text-muted">Deal detail view</p>
    </div>
  );
}
