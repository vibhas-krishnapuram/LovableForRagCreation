import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ragAPI } from '../services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Upload, X, FileText, ChevronLeft } from 'lucide-react';
import { motion } from 'framer-motion';

export const CreateRAG: React.FC = () => {
  const [ragName, setRagName] = useState('');
  const [model, setModel] = useState('claude');
  const [key, setKey] = useState('');
  const [documents, setDocuments] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setDocuments(Array.from(e.target.files));
    }
  };

  const removeDocument = (index: number) => {
    setDocuments(documents.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!ragName || !model || !key || documents.length === 0) {
      setError('Please fill in all fields and select at least one document');
      return;
    }

    setLoading(true);
    try {
      await ragAPI.create(ragName, model, key, documents);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create RAG instance');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')} className="p-0 hover:bg-transparent">
          <ChevronLeft className="h-4 w-4 mr-1" /> Back
        </Button>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Card className="border-border/50 shadow-lg">
          <CardHeader>
            <CardTitle>Create New RAG Instance</CardTitle>
            <CardDescription>
              Configure your new Retrieval-Augmented Generation instance with your documents.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md">
                  {error}
                </div>
              )}

              <div className="space-y-2">
                <label htmlFor="ragName" className="text-sm font-medium">RAG Name</label>
                <Input
                  id="ragName"
                  value={ragName}
                  onChange={(e) => setRagName(e.target.value)}
                  placeholder="My Knowledge Base"
                  required
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="model" className="text-sm font-medium">Model</label>
                <div className="relative">
                  <select
                    id="model"
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    required
                  >
                    <option value="claude">Claude (AWS Bedrock)</option>
                    <option value="openai">GPT-4 (OpenAI)</option>
                  </select>
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="key" className="text-sm font-medium">API Key</label>
                <Input
                  type="password"
                  id="key"
                  value={key}
                  onChange={(e) => setKey(e.target.value)}
                  placeholder="Enter your API key"
                  required
                />
                <p className="text-xs text-muted-foreground">
                  Your API key is encrypted and stored securely
                </p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Documents</label>
                <div className="border-2 border-dashed border-input rounded-lg p-6 hover:bg-muted/50 transition-colors text-center cursor-pointer relative">
                  <input
                    type="file"
                    id="documents"
                    multiple
                    onChange={handleFileChange}
                    accept=".pdf,.docx,.txt"
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    required={documents.length === 0}
                  />
                  <div className="flex flex-col items-center gap-2">
                    <Upload className="h-8 w-8 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">
                      Drag & drop files here or click to browse
                    </p>
                    <p className="text-xs text-muted-foreground/70">
                      Supported formats: PDF, DOCX, TXT
                    </p>
                  </div>
                </div>

                {documents.length > 0 && (
                  <div className="mt-4 space-y-2">
                    <p className="text-sm font-medium text-muted-foreground">Selected files:</p>
                    <div className="grid gap-2">
                      {documents.map((doc, idx) => (
                        <div key={idx} className="flex items-center justify-between p-2 bg-secondary/50 rounded-md text-sm border border-border">
                          <div className="flex items-center gap-2 overflow-hidden">
                            <FileText className="h-4 w-4 text-primary shrink-0" />
                            <span className="truncate">{doc.name}</span>
                          </div>
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6 text-muted-foreground hover:text-destructive"
                            onClick={() => removeDocument(idx)}
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="flex gap-4 pt-4">
                <Button
                  type="submit"
                  disabled={loading}
                  className="flex-1"
                >
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                      Creating...
                    </span>
                  ) : (
                    'Create RAG'
                  )}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/dashboard')}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};


