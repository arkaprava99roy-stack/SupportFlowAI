import React, { useEffect, useRef } from 'react';

export type AgentStateMode = 'idle' | 'thinking' | 'escalated';

interface AgentCanvas3DProps {
  mode?: AgentStateMode;
  className?: string;
  size?: number;
}

interface Point3D {
  x: number;
  y: number;
  z: number;
}

export const AgentCanvas3D: React.FC<AgentCanvas3DProps> = ({
  mode = 'idle',
  className = '',
  size = 320,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const mouseRef = useRef<{ x: number; y: number; isDown: boolean }>({ x: 0, y: 0, isDown: false });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Generate Icosahedron vertices
    const phi = (1 + Math.sqrt(5)) / 2;
    const rawVertices: Point3D[] = [
      { x: -1, y: phi, z: 0 },
      { x: 1, y: phi, z: 0 },
      { x: -1, y: -phi, z: 0 },
      { x: 1, y: -phi, z: 0 },
      { x: 0, y: -1, z: phi },
      { x: 0, y: 1, z: phi },
      { x: 0, y: -1, z: -phi },
      { x: 0, y: 1, z: -phi },
      { x: phi, y: 0, z: -1 },
      { x: phi, y: 0, z: 1 },
      { x: -phi, y: 0, z: -1 },
      { x: -phi, y: 0, z: 1 },
    ];

    // Normalize and scale vertices
    const radius = size * 0.36;
    const vertices: Point3D[] = rawVertices.map((v) => {
      const len = Math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
      return {
        x: (v.x / len) * radius,
        y: (v.y / len) * radius,
        z: (v.z / len) * radius,
      };
    });

    // Edges of icosahedron
    const edges: [number, number][] = [
      [0, 11], [0, 5], [0, 1], [0, 7], [0, 10],
      [1, 5], [5, 11], [11, 10], [10, 7], [7, 1],
      [3, 9], [3, 4], [3, 2], [3, 6], [3, 8],
      [4, 9], [9, 8], [8, 6], [6, 2], [2, 4],
      [5, 4], [5, 9], [1, 9], [1, 8], [7, 8],
      [7, 6], [10, 6], [10, 2], [11, 2], [11, 4]
    ];

    // Orbit particles
    const particleCount = 20;
    const particles = Array.from({ length: particleCount }).map(() => ({
      theta: Math.random() * Math.PI * 2,
      phi: (Math.random() - 0.5) * Math.PI,
      radius: radius * (1.15 + Math.random() * 0.45),
      speed: (0.004 + Math.random() * 0.008) * (Math.random() > 0.5 ? 1 : -1),
      size: 1 + Math.random() * 2,
      alpha: 0.2 + Math.random() * 0.6,
    }));

    let rotX = 0.2;
    let rotY = 0.3;
    let rotZ = 0;
    let animId: number;
    let pulse = 0;

    const render = () => {
      // Rotation speeds based on state mode
      let speedX = 0.003;
      let speedY = 0.006;
      let primaryColor = '20, 184, 166'; // Teal
      let coreColor = '45, 212, 191';
      let glowColor = 'rgba(20, 184, 166, 0.4)';

      if (mode === 'thinking') {
        speedX = 0.012;
        speedY = 0.022;
        primaryColor = '245, 158, 11'; // Amber
        coreColor = '251, 191, 36';
        glowColor = 'rgba(245, 158, 11, 0.6)';
      } else if (mode === 'escalated') {
        speedX = 0.008;
        speedY = 0.015;
        primaryColor = '239, 68, 68'; // Crimson
        coreColor = '248, 113, 113';
        glowColor = 'rgba(239, 68, 68, 0.65)';
      }

      rotX += speedX;
      rotY += speedY;
      pulse += 0.04;

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const cx = canvas.width / 2;
      const cy = canvas.height / 2;

      // Draw atmospheric background glow
      const bgGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius * 1.5);
      bgGrad.addColorStop(0, glowColor);
      bgGrad.addColorStop(0.5, `rgba(${primaryColor}, 0.08)`);
      bgGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = bgGrad;
      ctx.beginPath();
      ctx.arc(cx, cy, radius * 1.5, 0, Math.PI * 2);
      ctx.fill();

      // Transform and project vertices
      const cosX = Math.cos(rotX);
      const sinX = Math.sin(rotX);
      const cosY = Math.cos(rotY);
      const sinY = Math.sin(rotY);

      const projected = vertices.map((v) => {
        // Y rotation
        let x1 = v.x * cosY + v.z * sinY;
        let y1 = v.y;
        let z1 = -v.x * sinY + v.z * cosY;

        // X rotation
        let x2 = x1;
        let y2 = y1 * cosX - z1 * sinX;
        let z2 = y1 * sinX + z1 * cosX;

        // Perspective
        const scale = (radius * 2) / (radius * 2 + z2 * 0.6);
        return {
          x: cx + x2 * scale,
          y: cy + y2 * scale,
          z: z2,
          scale,
        };
      });

      // Draw wireframe edges
      edges.forEach(([i, j]) => {
        const p1 = projected[i];
        const p2 = projected[j];
        const avgZ = (p1.z + p2.z) / 2;
        const depthAlpha = Math.max(0.12, (avgZ + radius) / (radius * 2));

        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.strokeStyle = `rgba(${primaryColor}, ${depthAlpha * (mode === 'thinking' ? 0.75 : 0.45)})`;
        ctx.lineWidth = depthAlpha * 1.5;
        ctx.stroke();
      });

      // Draw vertex glowing nodes
      projected.forEach((p) => {
        const nodeAlpha = Math.max(0.2, (p.z + radius) / (radius * 2));
        const nodeSize = (mode === 'thinking' ? 3.5 : 2.5) * p.scale;

        // Glow ring
        ctx.beginPath();
        ctx.arc(p.x, p.y, nodeSize * 2.2, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${primaryColor}, ${nodeAlpha * 0.25})`;
        ctx.fill();

        // Node center
        ctx.beginPath();
        ctx.arc(p.x, p.y, nodeSize, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${coreColor}, ${nodeAlpha * 0.9})`;
        ctx.fill();
      });

      // Draw orbit floating particles
      particles.forEach((pt) => {
        pt.theta += pt.speed;
        const px = Math.cos(pt.theta) * Math.cos(pt.phi) * pt.radius;
        const py = Math.sin(pt.phi) * pt.radius;
        const pz = Math.sin(pt.theta) * Math.cos(pt.phi) * pt.radius;

        // Rotate
        let x1 = px * cosY + pz * sinY;
        let y1 = py;
        let z1 = -px * sinY + pz * cosY;

        let x2 = x1;
        let y2 = y1 * cosX - z1 * sinX;
        let z2 = y1 * sinX + z1 * cosX;

        const scale = (radius * 2) / (radius * 2 + z2 * 0.6);
        const scrX = cx + x2 * scale;
        const scrY = cy + y2 * scale;

        ctx.beginPath();
        ctx.arc(scrX, scrY, pt.size * scale, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${coreColor}, ${pt.alpha * Math.max(0.2, (z2 + radius) / (radius * 2))})`;
        ctx.fill();
      });

      // Center luminous energy core
      const corePulse = (Math.sin(pulse) + 1) * 0.5;
      const coreR = (radius * 0.18) + (corePulse * 4);
      const coreGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, coreR);
      coreGrad.addColorStop(0, `rgba(${coreColor}, 0.95)`);
      coreGrad.addColorStop(0.5, `rgba(${primaryColor}, 0.5)`);
      coreGrad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = coreGrad;
      ctx.beginPath();
      ctx.arc(cx, cy, coreR, 0, Math.PI * 2);
      ctx.fill();

      animId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animId);
    };
  }, [mode, size]);

  return (
    <div className={`relative flex items-center justify-center ${className}`}>
      <canvas
        ref={canvasRef}
        width={size}
        height={size}
        className="w-full h-full max-w-full aspect-square pointer-events-none"
      />
    </div>
  );
};
