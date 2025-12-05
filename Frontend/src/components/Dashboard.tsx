import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ragAPI } from '../services/api';
import type { RagListItem } from '../types';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Plus, Trash2, MessageSquare, Database } from 'lucide-react';
import { motion } from 'framer-motion';

export const Dashboard: React.FC = () => {
  const [rags, setRags] = useState<RagListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadRags();
  }, []);

  const loadRags = async () => {
    try {
      setLoading(true);
      const data = await ragAPI.list();
      setRags(data);
      setError('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load RAG instances');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (ragId: string) => {
    if (!window.confirm('Are you sure you want to delete this RAG instance?')) {
      return;
    }

    try {
      await ragAPI.delete(ragId);
      await loadRags();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete RAG instance');
    }
  };

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-1">Manage your RAG instances and knowledge bases.</p>
        </div>
        <Button onClick={() => navigate('/create')} className="gap-2">
          <Plus size={16} /> Create RAG
        </Button>
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive border border-destructive/20 px-4 py-3 rounded-md">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center p-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : rags.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <div className="rounded-full bg-primary/10 p-4 mb-4">
              <Database className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No RAG instances yet</h3>
            <p className="text-muted-foreground mb-6 max-w-sm">
              Create your first Retrieval-Augmented Generation instance to start querying your documents using AI.
            </p>
            <Button onClick={() => navigate('/create')}>Create Your First RAG</Button>
          </CardContent>
        </Card>
      ) : (
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {rags.map((rag) => (
            <motion.div key={rag.rag_id} variants={item}>
              <Card className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <CardTitle className="text-xl truncate" title={rag.rag_name}>{rag.rag_name}</CardTitle>
                  <div className="text-xs font-medium text-muted-foreground bg-secondary px-2 py-1 rounded inline-block w-fit mt-2">
                    {rag.model}
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    Start querying your documents with this RAG instance.
                  </p>
                </CardContent>
                <CardFooter className="gap-2">
                  <Button
                    className="flex-1 gap-2"
                    onClick={() => navigate(`/query/${rag.rag_id}`)}
                  >
                    <MessageSquare size={16} /> Query
                  </Button>
                  <Button
                    variant="destructive"
                    size="icon"
                    onClick={() => handleDelete(rag.rag_id)}
                  >
                    <Trash2 size={16} />
                  </Button>
                </CardFooter>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
};


