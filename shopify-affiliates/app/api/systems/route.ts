import { NextResponse } from 'next/server';
import { getSystems } from '@/lib/systems';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const systems = await getSystems();
    return NextResponse.json({ systems, checkedAt: new Date().toISOString() });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
