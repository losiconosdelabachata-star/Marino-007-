import { NextRequest, NextResponse } from 'next/server';
import { ACTIONS, startJob, recentJobs, getJob, stopJob } from '@/lib/jobs';

export const dynamic = 'force-dynamic';

/** Lists available actions, plus recent job history. */
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const jobId = searchParams.get('job');

  if (jobId) {
    const job = getJob(jobId);
    if (!job) return NextResponse.json({ error: 'No such job' }, { status: 404 });
    return NextResponse.json({ job });
  }

  return NextResponse.json({
    actions: Object.entries(ACTIONS).map(([id, s]) => ({
      id,
      label: s.label,
      danger: s.danger ?? null,
    })),
    jobs: recentJobs(),
  });
}

/** Starts an allowlisted action and returns the job to poll. */
export async function POST(request: NextRequest) {
  try {
    const { action } = await request.json();
    const result = startJob(action);

    if ('error' in result) {
      return NextResponse.json({ success: false, error: result.error }, { status: 400 });
    }

    return NextResponse.json({ success: true, job: result });
  } catch (error) {
    return NextResponse.json({ success: false, error: String(error) }, { status: 500 });
  }
}

/** Cancels a running job. */
export async function DELETE(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const jobId = searchParams.get('job');
  if (!jobId) {
    return NextResponse.json({ success: false, error: 'job id required' }, { status: 400 });
  }
  return NextResponse.json({ success: stopJob(jobId) });
}
