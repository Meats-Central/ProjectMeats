import React, { useCallback } from 'react';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  MiniMap,
  Controls,
  Background,
} from 'reactflow';
import 'reactflow/dist/style.css';
import styled from 'styled-components';

export interface WorkflowStage {
  id: string;
  label: string;
  status: 'pending' | 'active' | 'completed' | 'exception';
  description?: string;
}

interface PurchaseOrderWorkflowProps {
  stages: WorkflowStage[];
  height?: number;
}

const PurchaseOrderWorkflow: React.FC<PurchaseOrderWorkflowProps> = ({ stages, height = 400 }) => {
  // Create nodes from stages
  const initialNodes: Node[] = stages.map((stage, index) => ({
    id: stage.id,
    position: { x: index * 200, y: 100 },
    data: {
      label: (
        <StageNode status={stage.status}>
          <StageName>{stage.label}</StageName>
          {stage.description && <StageDescription>{stage.description}</StageDescription>}
          <StageStatus status={stage.status}>{getStatusIcon(stage.status)}</StageStatus>
        </StageNode>
      ),
    },
    style: {
      background: getNodeColor(stage.status),
      border: `2px solid ${getBorderColor(stage.status)}`,
      borderRadius: '8px',
      padding: '10px',
      width: 180,
    },
  }));

  // Create edges between consecutive stages
  const initialEdges: Edge[] = stages.slice(0, -1).map((stage, index) => ({
    id: `${stage.id}-${stages[index + 1].id}`,
    source: stage.id,
    target: stages[index + 1].id,
    animated: stages[index + 1].status === 'active',
    style: { stroke: '#6c757d' },
  }));

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <WorkflowContainer>
      <WorkflowTitle>Purchase Order Workflow</WorkflowTitle>
      <ReactFlowContainer style={{ height }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable={false}
          fitView
        >
          <MiniMap />
          <Controls />
          <Background />
        </ReactFlow>
      </ReactFlowContainer>
    </WorkflowContainer>
  );
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed':
      return '✓';
    case 'active':
      return '⏳';
    case 'exception':
      return '⚠️';
    default:
      return '○';
  }
};

const getNodeColor = (status: string) => {
  switch (status) {
    case 'completed':
      return '#d4edda';
    case 'active':
      return '#fff3cd';
    case 'exception':
      return '#f8d7da';
    default:
      return '#e2e3e5';
  }
};

const getBorderColor = (status: string) => {
  switch (status) {
    case 'completed':
      return '#28a745';
    case 'active':
      return '#ffc107';
    case 'exception':
      return '#dc3545';
    default:
      return '#6c757d';
  }
};

const WorkflowContainer = styled.div`
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
`;

const WorkflowTitle = styled.h3`
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
`;

const ReactFlowContainer = styled.div`
  border: 1px solid #dee2e6;
  border-radius: 4px;
`;

const StageNode = styled.div<{ status: string }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 8px;
`;

const StageName = styled.div`
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
  color: #2c3e50;
`;

const StageDescription = styled.div`
  font-size: 12px;
  color: #6c757d;
  margin-bottom: 8px;
`;

const StageStatus = styled.div<{ status: string }>`
  font-size: 20px;
  color: ${(props) => {
    switch (props.status) {
      case 'completed':
        return '#28a745';
      case 'active':
        return '#ffc107';
      case 'exception':
        return '#dc3545';
      default:
        return '#6c757d';
    }
  }};
`;

export default PurchaseOrderWorkflow;
