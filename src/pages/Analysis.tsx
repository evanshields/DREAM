import { useParams } from 'react-router-dom';

export default function Analysis() {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="p-8">
      <h1 className="text-3xl font-heading font-semibold mb-4">Analysis #{id}</h1>
      <p className="text-muted">Deal analysis view</p>
    </div>
  );
}
