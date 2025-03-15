import React, { useState } from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Download, Copy, RefreshCw, Table, BarChart3, FileJson, Database } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';
import AnimatedTransition from './AnimatedTransition';

function ResultsDisplay({ data, isLoading }) {
  const [displayMode, setDisplayMode] = useState('table');
  const { toast } = useToast();

  const handleCopyToClipboard = () => {
    if (!data) return;
    navigator.clipboard.writeText(JSON.stringify(data, null, 2))
      .then(() => {
        toast({
          title: "Copied to clipboard",
          description: "Dataset has been copied as JSON",
        });
      })
      .catch((err) => {
        console.error('Could not copy text: ', err);
        toast({
          title: "Failed to copy",
          description: "There was an error copying to clipboard",
          variant: "destructive",
        });
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

    toast({
      title: "Downloaded successfully",
      description: "Dataset has been downloaded as JSON",
    });
  };

  if (isLoading) {
    return (
      <Card className="w-full bg-synthesizer-surface border-synthesizer-border shadow-sm">
        <CardContent className="p-6">
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
      <Card className="w-full bg-synthesizer-surface border-synthesizer-border shadow-sm mt-6">
        <CardHeader className="pb-2">
          <div className="flex justify-between items-center">
            <div>
              <CardTitle className="text-lg font-medium text-synthesizer-text">Generated Dataset</CardTitle>
              <p className="text-sm text-synthesizer-text-secondary mt-1">
                {data.length} synthetic transactions generated
              </p>
            </div>
            <div className="flex space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleCopyToClipboard}
                className="border-synthesizer-border text-synthesizer-text-secondary"
              >
                <Copy className="h-4 w-4 mr-1" />
                Copy
              </Button>
              <Button
                size="sm"
                onClick={handleDownload}
                className="bg-synthesizer-accent hover:bg-synthesizer-accent-hover text-white"
              >
                <Download className="h-4 w-4 mr-1" />
                Download
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="px-6">
          <Tabs value={displayMode} onValueChange={setDisplayMode} className="w-full">
            <TabsList className="grid grid-cols-3 mb-4">
              <TabsTrigger value="table" className="text-sm">
                <Table className="h-4 w-4 mr-1" />
                Table View
              </TabsTrigger>
              <TabsTrigger value="json" className="text-sm">
                <FileJson className="h-4 w-4 mr-1" />
                JSON View
              </TabsTrigger>
              <TabsTrigger value="stats" className="text-sm">
                <BarChart3 className="h-4 w-4 mr-1" />
                Statistics
              </TabsTrigger>
            </TabsList>

            <TabsContent value="table" className="relative overflow-x-auto rounded-md border border-synthesizer-border">
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
            </TabsContent>

            <TabsContent value="json">
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
            </TabsContent>

            <TabsContent value="stats">
              <div className="bg-white p-4 rounded-md border border-synthesizer-border">
                <h4 className="font-medium text-synthesizer-text mb-3">Dataset Summary</h4>
                <div className="grid grid-cols-3 gap-4">
                  <StatCard
                    title="Total Records"
                    value={String(data.length)}
                    icon={<Table className="h-4 w-4 text-synthesizer-accent" />}
                  />
                  <StatCard
                    title="Fields"
                    value={String(fields.length)}
                    icon={<FileJson className="h-4 w-4 text-synthesizer-accent" />}
                  />
                  <StatCard
                    title="Data Size"
                    value={`~${Math.round(JSON.stringify(data).length / 1024)} KB`}
                    icon={<Database className="h-4 w-4 text-synthesizer-accent" />}
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
            </TabsContent>
          </Tabs>
        </CardContent>

        <CardFooter className="pt-2 pb-6 px-6">
          <p className="text-xs text-synthesizer-text-tertiary">
            This data is synthetically generated and does not represent real transactions.
          </p>
        </CardFooter>
      </Card>
    </AnimatedTransition>
  );
}

function StatCard({ title, value, icon }) {
  return (
    <div className="bg-synthesizer-soft p-3 rounded-md">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-medium text-synthesizer-text-secondary">{title}</span>
        {icon}
      </div>
      <div className="text-lg font-semibold text-synthesizer-text">{value}</div>
    </div>
  );
}

export default ResultsDisplay;
