type Props = {
  value: string;
  onChange: (value: string) => void;
};

const filters = ['all', 'streak', 'total', 'frequency'];

export const GoalFilterTabs = ({ value, onChange }: Props) => {
  return (
    <div className="flex gap-2 mb-4">
      {filters.map((f) => (
        <button
          key={f}
          onClick={() => onChange(f)}
          className={`px-3 py-1 rounded ${
            value === f ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          {f}
        </button>
      ))}
    </div>
  );
};
