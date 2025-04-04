import React, { useState } from 'react';

// Material UI Card components
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import CardHeader from '@mui/material/CardHeader';

// Material UI Button component
import Button from '@mui/material/Button';

// Material UI Tabs components
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';

// Material UI Badge component
import Badge from '@mui/material/Badge';

// Lucide-react icons remain the same
import { Download, Copy, RefreshCw, Table, BarChart3, FileJson, Database } from 'lucide-react';

// React-Toastify for notifications
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Replace your custom "cn" utility with the classnames package
import classNames from 'classnames';

// Import your custom animated transition component
import AnimatedTransition from './AnimatedTransition';

// Optionally initialize ToastContainer somewhere in your app root:
// import { ToastContainer } from 'react-toastify';
// <ToastContainer />

function ResultsDisplay({ data, isLoading }) {
  const [displayMode, setDisplayMode] = useState('table');

  const handleCopyToClipboard = () => {
    if (!data) return;
    navigator.clipboard.writeText(JSON.stringify(data, null, 2))
      .then(() => {
        toast.success("Dataset has been copied as JSON");
      })
      .catch((err) => {
        console.error('Could not copy text: ', err);
        toast.error("There was an error copying to clipboard");
      });
  };

  const handleDownload = () => {
    if (!data) return;
    const jsonString = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'synthetic_transactions.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    toast.success("Dataset has been downloaded as JSON");
  };

  if (isLoading) {
    return (
      <Card sx={{ width: '100%' }} className="bg-synthesizer-surface border-synthesizer-border shadow-sm">
        <CardContent>
          <div className="flex flex-col items-center justify-center py-10">
            <RefreshCw className="h-10 w-10 text-synthesizer-accent animate-spin mb-4" />
            <h3 className="text-lg font-medium text-synthesizer-text">Generating Dataset</h3>
            <p className="text-sm text-synthesizer-text-secondary mt-2 max-w-md text-center">
              Our model is synthesizing transaction data based on your parameters. This may take a moment...
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return null;
  }

  const sampleData = data.slice(0, 10);
  const fields = Object.keys(data[0] || {});

  return (
    <AnimatedTransition animationType="scale">
      <Card sx={{ width: '100%', mt: 2 }} className="bg-synthesizer-surface border-synthesizer-border shadow-sm">
        <CardHeader
          title="Generated Dataset"
          subheader={`${data.length} synthetic transactions generated`}
          action={
            <div>
              <Button variant="outlined" size="small" onClick={handleCopyToClipboard} sx={{ mr: 1 }}>
                <Copy style={{ marginRight: 4 }} />
                Copy
              </Button>
              <Button variant="contained" size="small" onClick={handleDownload}>
                <Download style={{ marginRight: 4 }} />
                Download
              </Button>
            </div>
          }
          sx={{ pb: 2 }}
        />

        <CardContent>
          <Tabs
            value={displayMode}
            onChange={(event, newValue) => setDisplayMode(newValue)}
            variant="fullWidth"
            sx={{ mb: 2 }}
          >
            <Tab
              value="table"
              label={
                <span>
                  <Table style={{ marginRight: 4 }} />
                  Table View
                </span>
              }
            />
            <Tab
              value="json"
              label={
                <span>
                  <FileJson style={{ marginRight: 4 }} />
                  JSON View
                </span>
              }
            />
            <Tab
              value="stats"
              label={
                <span>
                  <BarChart3 style={{ marginRight: 4 }} />
                  Statistics
                </span>
              }
            />
          </Tabs>

          {displayMode === 'table' && (
            <div className="relative overflow-x-auto rounded-md border border-synthesizer-border">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-synthesizer-text-secondary uppercase bg-synthesizer-soft">
                  <tr>
                    {fields.map(field => (
                      <th key={field} className="px-4 py-3">
                        {field}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {sampleData.map((row, index) => (
                    <tr
                      key={index}
                      className={
                        index % 2 === 0
                          ? "bg-white border-b border-synthesizer-border"
                          : "bg-synthesizer-surface-hover border-b border-synthesizer-border"
                      }
                    >
                      {fields.map(field => (
                        <td key={`${index}-${field}`} className="px-4 py-2.5 text-synthesizer-text">
                          {typeof row[field] === 'object'
                            ? JSON.stringify(row[field])
                            : String(row[field])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              {data.length > 10 && (
                <div className="px-4 py-2 text-xs text-synthesizer-text-secondary bg-synthesizer-soft border-t border-synthesizer-border">
                  Showing 10 of {data.length} records
                </div>
              )}
            </div>
          )}

          {displayMode === 'json' && (
            <div className="bg-[#1e1e1e] text-white p-4 rounded-md overflow-x-auto max-h-96">
              <pre className="text-xs">
                {JSON.stringify(sampleData, null, 2)}
              </pre>
              {data.length > 10 && (
                <div className="mt-2 pt-2 text-xs text-gray-400 border-t border-gray-700">
                  Showing 10 of {data.length} records
                </div>
              )}
            </div>
          )}

          {displayMode === 'stats' && (
            <div className="bg-white p-4 rounded-md border border-synthesizer-border">
              <h4 className="font-medium text-synthesizer-text mb-3">Dataset Summary</h4>
              <div className="grid grid-cols-3 gap-4">
                <StatCard
                  title="Total Records"
                  value={String(data.length)}
                  icon={<Table style={{ color: '#7c3aed', height: 16, width: 16 }} />}
                />
                <StatCard
                  title="Fields"
                  value={String(fields.length)}
                  icon={<FileJson style={{ color: '#7c3aed', height: 16, width: 16 }} />}
                />
                <StatCard
                  title="Data Size"
                  value={`~${Math.round(JSON.stringify(data).length / 1024)} KB`}
                  icon={<Database style={{ color: '#7c3aed', height: 16, width: 16 }} />}
                />
              </div>

              <h4 className="font-medium text-synthesizer-text mt-6 mb-3">Field Types</h4>
              <div className="flex flex-wrap gap-2">
                {fields.map(field => {
                  const item = data.find(row => row[field] !== null);
                  let typeName = typeof (item ? item[field] : null);
                  if (Array.isArray(item ? item[field] : null)) {
                    typeName = "array";
                  }

                  return (
                    <Badge
                      key={field}
                      className="bg-synthesizer-soft text-synthesizer-text hover:bg-synthesizer-soft"
                    >
                      {field}: <span className="ml-1 opacity-70">{typeName}</span>
                    </Badge>
                  );
                })}
              </div>
            </div>
          )}
        </CardContent>

        <CardActions sx={{ pt: 2, pb: 6, px: 2 }}>
          <p className="text-xs text-synthesizer-text-tertiary">
            This data is synthetically generated and does not represent real transactions.
          </p>
        </CardActions>
      </Card>
    </AnimatedTransition>
  );
}

function StatCard({ title, value, icon }) {
  return (
    <Card variant="outlined" sx={{ p: 1 }}>
      <CardContent sx={{ p: 1 }}>
        <div className="flex items-center justify-between mb-1">
          <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>{title}</span>
          {icon}
        </div>
        <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#111827' }}>
          {value}
        </div>
      </CardContent>
    </Card>
  );
}

export default ResultsDisplay;
