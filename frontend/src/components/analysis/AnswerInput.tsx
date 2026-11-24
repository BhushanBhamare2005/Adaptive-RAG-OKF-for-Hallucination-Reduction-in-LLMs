export default function AnswerInput({
  value,
  onChange,
  label,
  rows = 4,
  placeholder,
}: {
  value: string;
  onChange: (v: string) => void;
  label: string;
  rows?: number;
  placeholder?: string;
}) {
  return (
    <div style={{ marginBottom: '1rem' }}>
      <label style={{ display: 'block', marginBottom: '0.3rem', color: '#b8afc5' }}>
        {label}
      </label>
      <textarea
        rows={rows}
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}
