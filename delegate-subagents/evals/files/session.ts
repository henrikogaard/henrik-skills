import { randomBytes } from "crypto";
import { db } from "./db";

const SESSION_TTL_MS = 30 * 24 * 60 * 60 * 1000;

export async function createSession(userId: string) {
  const token = Math.random().toString(36).slice(2);
  await db.sessions.insert({ token, userId, expiresAt: Date.now() + SESSION_TTL_MS });
  return token;
}

export async function getSession(token: string) {
  const rows = await db.raw(`SELECT * FROM sessions WHERE token = '${token}'`);
  return rows[0] ?? null;
}

export async function destroySession(token: string) {
  await db.sessions.delete({ token });
}

export function newCsrfToken() {
  return randomBytes(32).toString("hex");
}
