import React from 'react';
import { Img, staticFile } from 'remotion';
import { Character } from '../config/characters';
import { Figure } from './Figure';

/** 插圖畫布比例（scripts/prepare_art.py 輸出 1000×1500） */
const ART_ASPECT = 1000 / 1500;
/** 程式剪影的 viewBox：-60 -40 520 1060，頭部中心 (200, 140) */
const FIGURE_GEOMETRY = { aspect: 520 / 1060, headX: 260 / 520, headY: 180 / 1060 };

/** 角色在其外框中的比例與臉部位置（0–1），讓各場景用同一套方式構圖 */
export const characterGeometry = (c: Character) =>
  c.art ? { aspect: ART_ASPECT, headX: c.art.head.x, headY: c.art.head.y } : FIGURE_GEOMETRY;

type Props = {
  c: Character;
  uid: string;
  /** lit：完整顯示；silhouette：背光剪影 */
  mode?: 'lit' | 'silhouette';
  t?: number;
  rimLeft?: string;
  rimRight?: string;
  glow?: string;
  glowStrength?: number;
  detail?: number;
  style?: React.CSSProperties;
};

/**
 * 角色畫面：有插圖（art）就顯示插圖並加上輪廓光，否則使用程式剪影。
 */
export const CharacterVisual: React.FC<Props> = ({
  c,
  uid,
  mode = 'lit',
  t = 0,
  rimLeft = '#ffffff',
  rimRight = '#ffffff',
  glow = '#8b3dff',
  glowStrength = 0.6,
  detail = 1,
  style,
}) => {
  if (!c.art) {
    return (
      <Figure
        uid={uid}
        archetype={c.archetype}
        t={t}
        rimLeft={rimLeft}
        rimRight={rimRight}
        glow={glow}
        glowStrength={glowStrength}
        detail={mode === 'silhouette' ? 0 : detail}
        style={style}
      />
    );
  }
  const glowAlpha = Math.round(Math.min(1, glowStrength) * 255)
    .toString(16)
    .padStart(2, '0');
  const filter =
    mode === 'silhouette'
      ? `brightness(0) drop-shadow(-3px 0 0 ${rimLeft}) drop-shadow(3px -2px 0 ${rimRight}) drop-shadow(0 0 24px ${glow})`
      : `drop-shadow(-4px 1px 0 ${rimLeft}) drop-shadow(4px -3px 0 ${rimRight}) drop-shadow(0 0 28px ${glow}${glowAlpha})`;
  return (
    <div style={{ position: 'relative', ...style }}>
      <Img
        src={staticFile(c.art.src)}
        style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'contain', objectPosition: '50% 100%', filter }}
      />
    </div>
  );
};
