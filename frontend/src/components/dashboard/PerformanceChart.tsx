import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from 'recharts';

export default function PerformanceChart({ data }: { data: any[] }) {
  return (
    <div className="card" style={{ height: 340 }}>
      <ResponsiveContainer>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#352044" />
          <XAxis dataKey="model" stroke="#b8afc5" />
          <YAxis stroke="#b8afc5" domain={[0, 1]} />
          <Tooltip
            contentStyle={{ background: '#100122', border: '1px solid #352044', color: '#ffffff' }}
          />
          <Legend />
          <Bar dataKey="accuracy" fill="#00e5a0" />
          <Bar dataKey="f1" fill="#06d6e0" />
          <Bar dataKey="roc_auc" fill="#e9f542" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
