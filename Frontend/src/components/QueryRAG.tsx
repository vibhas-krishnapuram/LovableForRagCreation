import { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ragAPI } from '../services/api';
import type { RagListItem } from '../types';
import { Card, CardContent } from './ui/Card';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Send, Upload, ChevronLeft, Bot, User, FileText, X } from 'lucide-react'; // Added X here

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export const QueryRAG: React.FC = () => {
  const { ragId } = useParams<{ ragId: string }>();
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([]); // Added state for chat history simulation
  const [loading, setLoading] = useState(false);
  const [ragInfo, setRagInfo] = useState<RagListItem | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const navigate = useNavigate();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadRagInfo();
  }, [ragId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadRagInfo = async () => {
    if (!ragId) return;
    try {
      const rags = await ragAPI.list();
      const rag = rags.find((r) => r.rag_id === ragId);
      setRagInfo(rag || null);
    } catch (err) {
      console.error('Failed to load RAG info', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ragId || (!query.trim() && !file)) return;

    const currentQuery = query;
    const currentFile = file;

    // Add user message immediately
    setMessages(prev => [...prev, { role: 'user', content: currentQuery + (currentFile ? ` [Attached: ${currentFile.name}]` : '') }]);
    setQuery('');
    setFile(null);
    setLoading(true);

    try {
      const result = currentFile
        ? await ragAPI.fileQuery(ragId, currentQuery, currentFile)
        : await ragAPI.query(ragId, currentQuery);

      setMessages(prev => [...prev, { role: 'assistant', content: result.response || 'No response received' }]);
    } catch (err: any) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error: Failed to get response.' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddDocs = async () => {
    if (!ragId) return;
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = '.pdf,.docx,.txt';
    input.onchange = async (e) => {
      const files = (e.target as HTMLInputElement).files;
      if (files && files.length > 0) {
        try {
          await ragAPI.addDocs(ragId, Array.from(files));
          alert('Documents added successfully!');
        } catch (err: any) {
          alert(err.response?.data?.detail || 'Failed to add documents');
        }
      }
    };
    input.click();
  };

  return (
    <div className="flex flex-col h-[calc(100vh-theme(spacing.24))]">
      <div className="flex items-center justify-between mb-4 px-4 sm:px-0">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')}>
            <ChevronLeft className="h-4 w-4 mr-1" /> Back
          </Button>
          {ragInfo && (
            <div className="flex flex-col">
              <h1 className="text-lg font-bold">{ragInfo.rag_name}</h1>
              <span className="text-xs text-muted-foreground uppercase tracking-wider">{ragInfo.model}</span>
            </div>
          )}
        </div>
        <Button variant="outline" size="sm" onClick={handleAddDocs} className="gap-2">
          <Upload className="h-4 w-4" /> Add Docs
        </Button>
      </div>

      <Card className="flex-1 flex flex-col min-h-0 border-border/50 shadow-sm overflow-hidden bg-background/50 backdrop-blur-sm">
        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-8 text-muted-foreground opacity-50">
              <Bot className="h-12 w-12 mb-4" />
              <p className="text-lg font-medium">Start a conversation</p>
              <p className="text-sm">Ask questions about your documents</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                    <Bot className="h-5 w-5 text-primary" />
                  </div>
                )}
                <div
                  className={`rounded-lg p-3 max-w-[80%] text-sm ${msg.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-foreground'
                    }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
                {msg.role === 'user' && (
                  <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center shrink-0">
                    <User className="h-5 w-5" />
                  </div>
                )}
              </div>
            ))
          )}
          {loading && (
            <div className="flex gap-3">
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                <Bot className="h-5 w-5 text-primary" />
              </div>
              <div className="bg-muted rounded-lg p-3 flex items-center gap-2">
                <span className="h-2 w-2 bg-primary/50 rounded-full animate-bounce" />
                <span className="h-2 w-2 bg-primary/50 rounded-full animate-bounce [animation-delay:0.2s]" />
                <span className="h-2 w-2 bg-primary/50 rounded-full animate-bounce [animation-delay:0.4s]" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </CardContent>

        <div className="p-4 border-t bg-background/50">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <div className="relative flex-1">
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a question..."
                className="pr-10"
                disabled={loading}
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="absolute right-1 top-1 h-8 w-8 text-muted-foreground hover:text-foreground"
                onClick={() => document.getElementById('query-file')?.click()}
              >
                <Upload className="h-4 w-4" />
              </Button>
              <input
                id="query-file"
                type="file"
                className="hidden"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                accept=".pdf,.docx,.txt"
              />
            </div>
            <Button type="submit" disabled={loading || (!query && !file)} size="icon">
              <Send className="h-4 w-4" />
            </Button>
          </form>
          {file && (
            <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground bg-secondary/50 p-1.5 rounded-md w-fit">
              <FileText className="h-3 w-3" />
              <span>{file.name}</span>
              <button onClick={() => setFile(null)} className="ml-1 hover:text-destructive">
                <X className="h-3 w-3" />
              </button>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};


