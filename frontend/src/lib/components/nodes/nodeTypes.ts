import type { NodeTypes } from '@xyflow/svelte';
import ConditionNode from './ConditionNode/ConditionNode.svelte';
import EntryNode from './EntryNode.svelte';
import ExitNode from './ExitNode.svelte';

export const nodeTypes: NodeTypes = {
	condition: ConditionNode,
	entry: EntryNode,
	exit: ExitNode
};
