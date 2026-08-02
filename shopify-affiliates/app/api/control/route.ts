import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import { projectRoot } from '@/lib/systems';

/**
 * Strict allowlist. The client sends an action id only - never a path or
 * argument - so no request can steer this into running arbitrary commands.
 */
const ACTIONS: Record<string, { cmd: string; args: string[]; label: string }> = {
  'blog:run': {
    cmd: 'python',
    args: ['blog_scheduler.py', '--once'],
    label: 'Generate today\'s blog post',
  },
  'orders:sweep': {
    cmd: 'python',
    args: ['order_automation.py', '--once'],
    label: 'Sweep Shopify for new orders',
  },
  'whatsapp:start': {
    cmd: 'node',
    args: ['whatsapp_server.js'],
    label: 'Start the WhatsApp bridge',
  },
};

export async function POST(request: NextRequest) {
  try {
    const { action } = await request.json();
    const spec = ACTIONS[action];

    if (!spec) {
      return NextResponse.json(
        { success: false, error: `Unknown action: ${action}` },
        { status: 400 }
      );
    }

    // Detached so the job outlives this request/response cycle.
    const child = spawn(spec.cmd, spec.args, {
      cwd: projectRoot(),
      detached: true,
      stdio: 'ignore',
      shell: process.platform === 'win32',
    });
    child.unref();

    return NextResponse.json({
      success: true,
      action,
      label: spec.label,
      startedAt: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json({ success: false, error: String(error) }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({
    actions: Object.entries(ACTIONS).map(([id, s]) => ({ id, label: s.label })),
  });
}
